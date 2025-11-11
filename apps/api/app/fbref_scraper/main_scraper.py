#!/usr/bin/env python3
"""Main scraper script for FBRef data extraction with CLI support."""

import time
from datetime import date, timedelta
from sqlalchemy.orm import joinedload

from .core import get_logger
from .core.cli_parser import parse_arguments, parse_nations, parse_date
from .core.progress_manager import (
    save_scraping_progress,
    clear_scraping_progress,
    get_scrapers_to_run
)
from .core.revalidation import trigger_revalidation
from app.core.database import Session as DBSession
from app.models import Competition, Nation, Season
from .scrapers import (
    SeasonsScraper,
    TeamStatsScraper,
    PlayersScraper,
    MatchesScraper,
    EventsScraper
)

logger = get_logger('main_scraper')


def run_initial_mode(args):
    """Run scraper in initial mode (full scrape)."""
    logger.info("Starting initial mode")
    
    nations = parse_nations(args.nations) if args.nations else None
    scrapers_to_run = get_scrapers_to_run(args.resume)
    
    for scraper_name, scraper_class in scrapers_to_run:
        try:
            logger.info(f"Running {scraper_name} scraper...")
            scraper = scraper_class()
            
            if scraper_name == 'nations':
                scraper.run()
            elif scraper_name in ['seasons', 'team_stats', 'players']:
                scraper.run(nations=nations, from_year=args.from_year, to_year=args.to_year)
            elif scraper_name in ['matches', 'events']:
                scraper.run(nations=nations, from_date=None, to_date=None)
            else:
                scraper.run(nations=nations)
            
            save_scraping_progress(scraper_name, completed=True)
            logger.info(f"{scraper_name} scraper completed successfully")
            
        except Exception as e:
            logger.error(f"{scraper_name} scraper failed: {e}")
            save_scraping_progress(scraper_name, completed=False)
            if not args.continue_on_error:
                raise
    
    clear_scraping_progress()
    
    logger.info("Triggering Next.js cache revalidation...")
    trigger_revalidation()


def run_daily_mode(args):
    """Run scraper in daily mode (update stats for most recent season)."""
    logger.info("Starting daily mode")
    
    if args.from_date and args.to_date:
        from_date = parse_date(args.from_date)
        to_date = parse_date(args.to_date)
    else:
        to_date = date.today()
        from_date = to_date - timedelta(days=args.days - 1)
    
    logger.info(f"Scraping data from {from_date} to {to_date}")
    
    nations = parse_nations(args.nations) if args.nations else None
    competitions = _get_competitions_for_nations(nations)
    
    for competition in competitions:
        logger.info(f"Processing daily updates for {competition.name}")
        
        db_most_recent = _get_most_recent_season_from_db(competition)
        if not db_most_recent:
            logger.warning(f"No seasons found for {competition.name}. Run initial mode first.")
            continue
        
        fbref_season = _get_current_season_from_fbref(competition)
        if not fbref_season:
            logger.warning(f"Could not scrape seasons from FBRef for {competition.name}")
            continue
        
        fbref_start_year, _ = fbref_season
        _verify_seasons_match(db_most_recent, fbref_start_year, competition.name)
        
        nation_name = competition.nation.name
        _update_stats_for_season(competition, db_most_recent, nation_name)
    
    logger.info("Adding new matches and events...")
    matches_scraper = MatchesScraper()
    matches_scraper.run(nations=nations, from_date=from_date, to_date=to_date)
    
    events_scraper = EventsScraper()
    events_scraper.run(nations=nations, from_date=from_date, to_date=to_date)
    
    logger.info("Daily mode completed successfully")
    
    logger.info("Triggering Next.js cache revalidation...")
    trigger_revalidation()


def run_seasonal_mode(args):
    """Run scraper in seasonal mode (handle new seasons and URL changes)."""
    logger.info("Starting seasonal mode")
    
    nations = parse_nations(args.nations) if args.nations else None
    competitions = _get_competitions_for_nations(nations)
    
    for competition in competitions:
        logger.info(f"Processing seasonal updates for {competition.name}")
        
        seasons_scraper = SeasonsScraper()
        seasons_scraper.run(nations=[competition.nation.name], seasonal_mode=True)
        
        team_stats_scraper = TeamStatsScraper()
        team_stats_scraper.run(nations=[competition.nation.name], seasonal_mode=True)
        
        players_scraper = PlayersScraper()
        players_scraper.run(nations=[competition.nation.name], seasonal_mode=True)
    
    logger.info("Seasonal mode completed successfully")
    
    logger.info("Triggering Next.js cache revalidation...")
    trigger_revalidation()


def _get_competitions_for_nations(nations):
    """Get all competitions for the specified nations."""
    session = DBSession()
    query = session.query(Competition).join(Nation).options(joinedload(Competition.nation))
    if nations:
        query = query.filter(Nation.name.in_(nations))
    competitions = query.all()
    session.close()
    return competitions


def _get_most_recent_season_from_db(competition):
    """Get the most recent season from database for a competition."""
    session = DBSession()
    return session.query(Season).filter_by(competition_id=competition.id).order_by(Season.start_year.desc()).first()


def _get_current_season_from_fbref(competition):
    """Get the current season from FBRef for a competition."""
    seasons_scraper = SeasonsScraper()
    seasons_scraper.load_page(f"{seasons_scraper.config.FBREF_BASE_URL}{competition.fbref_url}")
    
    df_list = seasons_scraper.fetch_html_table(f"{seasons_scraper.config.FBREF_BASE_URL}{competition.fbref_url}")
    if not df_list:
        return None
    
    fbref_seasons = df_list[0].iloc[::-1]
    most_recent_fbref = fbref_seasons.iloc[-1]
    
    season_str = str(most_recent_fbref['Season'])
    if '-' in season_str:
        start_year, end_year = map(int, season_str.split('-'))
    else:
        start_year = int(season_str[:4])
        end_year = int(season_str[:4])
    
    return start_year, end_year


def _verify_seasons_match(db_season, fbref_start_year, competition_name):
    """Verify that database season matches FBRef current season."""
    if db_season.start_year != fbref_start_year:
        logger.error(f"Season mismatch for {competition_name}: DB has {db_season.start_year}-{db_season.end_year}, FBRef shows {fbref_start_year}-{fbref_start_year + 1}")
        logger.error("Run seasonal mode first to handle new seasons.")
        raise Exception("Season mismatch detected - run seasonal mode first")
    
    logger.info(f"Seasons match for {competition_name}: {db_season.start_year}-{db_season.end_year}")


def _update_stats_for_season(competition, season, nation_name):
    """Update team and player stats for a specific season."""
    logger.info(f"Updating team stats for {competition.name} {season.start_year}-{season.end_year}")
    team_stats_scraper = TeamStatsScraper()
    team_stats_scraper.run(nations=[nation_name], from_year=season.start_year, to_year=season.end_year, update_mode=True)
    
    logger.info(f"Updating player stats for {competition.name} {season.start_year}-{season.end_year}")
    players_scraper = PlayersScraper()
    players_scraper.run(nations=[nation_name], from_year=season.start_year, to_year=season.end_year, update_mode=True)


def main():
    """Main entry point."""
    args = parse_arguments()
    
    logger.info(f"Starting FBRef scraper in {args.mode} mode")
    
    start_time = time.time()
    
    try:
        if args.mode == 'initial':
            run_initial_mode(args)
        elif args.mode == 'daily':
            run_daily_mode(args)
        elif args.mode == 'seasonal':
            run_seasonal_mode(args)
            
        end_time = time.time()
        elapsed_time = round((end_time - start_time) / 60, 1)
        
        logger.info(f"FBRef scraping completed successfully! Process took {elapsed_time} minutes")
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user. Progress has been saved and can be resumed.")
        logger.info("To resume, run the same command with --resume flag")
        return
    except Exception as e:
        logger.error(f"Scraping failed with error: {e}")
        if args.continue_on_error:
            logger.info("Continuing despite error due to --continue-on-error flag")
        else:
            logger.info("To resume from where it failed, run the same command with --resume flag")
            raise


if __name__ == "__main__":
    main()
