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
from app.models import Competition, Nation, Season, Match, Event
from app.core.goal_value import EventGoalValueUpdater, PlayerStatsGoalValueUpdater
from app.core.goal_value.utils import get_scoring_team_id
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
                scraper.run(nations=nations, from_date=None, to_date=None, from_year=args.from_year, to_year=args.to_year)
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
    
    current_season_years = set()
    for competition in competitions:
        db_most_recent = _get_most_recent_season_from_db(competition)
        if db_most_recent:
            current_season_years.add(db_most_recent.start_year)
    
    if not current_season_years:
        logger.warning("No current seasons found. Run initial mode first.")
        return
    
    from_year = min(current_season_years)
    to_year = max(current_season_years)
    
    logger.info(f"Filtering matches/events for seasons with start_year between {from_year} and {to_year}")
    logger.info("Adding new matches and events...")
    matches_scraper = MatchesScraper()
    matches_scraper.run(nations=nations, from_date=from_date, to_date=to_date, from_year=from_year, to_year=to_year)
    
    session = DBSession()
    matches_in_range = session.query(Match).options(
        joinedload(Match.season)
    ).filter(
        Match.date >= from_date,
        Match.date <= to_date
    ).all()
    
    if not matches_in_range:
        logger.info("No matches found in date range. Nothing to update.")
        session.close()
        return
    
    competition_ids = set()
    team_ids = set()
    for match in matches_in_range:
        competition_ids.add(match.season.competition_id)
        team_ids.add(match.home_team_id)
        team_ids.add(match.away_team_id)
    
    session.close()
    
    logger.info(f"Found {len(competition_ids)} competitions and {len(team_ids)} teams with matches in date range")
    
    for competition in competitions:
        if competition.id not in competition_ids:
            continue
            
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
        
        logger.info(f"Updating team stats for {competition.name} {db_most_recent.start_year}-{db_most_recent.end_year}")
        team_stats_scraper = TeamStatsScraper()
        team_stats_scraper.run(
            nations=[nation_name], 
            from_year=db_most_recent.start_year, 
            to_year=db_most_recent.start_year,
            update_mode=True
        )
        
        logger.info(f"Updating player stats for {len(team_ids)} teams in {competition.name}")
        players_scraper = PlayersScraper()
        players_scraper.run(
            nations=[nation_name], 
            from_year=db_most_recent.start_year, 
            to_year=db_most_recent.start_year,
            update_mode=True,
            team_ids=team_ids
        )
    
    logger.info(f"Scraping events for {len(team_ids)} teams...")
    events_scraper = EventsScraper()
    events_scraper.run(nations=nations, from_date=from_date, to_date=to_date, from_year=from_year, to_year=to_year, team_ids=team_ids)
    
    session = DBSession()
    new_goal_events = session.query(
        Event.id, 
        Event.player_id, 
        Event.event_type,
        Event.home_team_goals_post_event, 
        Event.home_team_goals_pre_event, 
        Event.away_team_goals_post_event,
        Event.away_team_goals_pre_event,
        Match.season_id,
        Match.home_team_id,
        Match.away_team_id
    ).join(Match).filter(
        Event.event_type.in_(['goal', 'own goal']),
        Event.goal_value.is_(None),
        Match.date >= from_date,
        Match.date <= to_date
    ).all()
    session.close()
    
    if new_goal_events:
        logger.info(f"Found {len(new_goal_events)} new goal events to update")
        
        event_ids = [event.id for event in new_goal_events]
        logger.info("Updating goal values for new events...")
        event_updater = EventGoalValueUpdater()
        event_updater.update_goal_values_for_events(event_ids)
        
        player_combinations = set()
        for event in new_goal_events:
            if event.player_id is None or event.event_type != 'goal':
                continue
            
            team_id = get_scoring_team_id(
                event.home_team_goals_post_event,
                event.home_team_goals_pre_event,
                event.away_team_goals_post_event,
                event.away_team_goals_pre_event,
                event.home_team_id,
                event.away_team_id
            )
            
            if team_id is None:
                continue
            
            player_combinations.add((event.player_id, event.season_id, team_id))
        
        if player_combinations:
            logger.info(f"Updating player stats for {len(player_combinations)} player-season-team combinations...")
            player_updater = PlayerStatsGoalValueUpdater()
            player_updater.update_player_stats_for_combinations(list(player_combinations))
    else:
        logger.info("No new goal events found to update")
    
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
    try:
        return session.query(Season).filter_by(competition_id=competition.id).order_by(Season.start_year.desc()).first()
    finally:
        session.close()


def _get_current_season_from_fbref(competition):
    """Get the current season from FBRef for a competition."""
    seasons_scraper = SeasonsScraper()
    base_url = seasons_scraper.config.FBREF_BASE_URL
    url = f"{base_url}{competition.fbref_url}"
    seasons_scraper.load_page(url)
    
    df_list = seasons_scraper.fetch_html_table(url)
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
