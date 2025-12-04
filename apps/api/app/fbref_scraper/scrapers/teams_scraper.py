"""Teams scraper for FBRef data extraction."""

from app.models import Nation, Team

from ..core import WebScraper, get_config, get_rate_limit, get_selected_nations


class TeamsScraper(WebScraper):
    def scrape(self, nations: list[str] | None = None) -> None:
        """Scrape team data."""
        nations = nations or get_selected_nations()

        config = get_config()
        all_nations = self.session.query(Nation).filter(Nation.name.in_(nations)).all()

        for nation in all_nations:
            nation = self.session.merge(nation)
            self.log_progress(f"Processing teams for {nation.name}")

            url = f"{config.FBREF_BASE_URL}{nation.clubs_url}"
            self.load_page(url)

            df_list = self.fetch_html_table(url, get_rate_limit("heavy"))

            if not df_list:
                self.log_progress(f"No teams found for {nation.name}")
                continue

            for team_tuple in df_list[0].iterrows():
                team_data = team_tuple[1]

                a_tags = self.find_elements("a", string=team_data["Squad"])
                if len(a_tags) == 1:
                    fbref_url = a_tags[0]["href"]
                elif len(a_tags) > 1:
                    for a_tag in a_tags:
                        tr = a_tag.parent.parent
                        tr_gender = tr.find("td", {"data-stat": "gender"})
                        if tr_gender and tr_gender.get_text(strip=True) == team_data["Gender"]:
                            fbref_url = a_tag["href"]
                            break
                else:
                    self.log_error("team scraping", Exception("No <a> tags found"))
                    continue

                team_fbref_id = self.extract_fbref_id(fbref_url)

                team_dict = {
                    "name": team_data["Squad"],
                    "gender": team_data["Gender"],
                    "fbref_id": team_fbref_id,
                    "fbref_url": fbref_url,
                    "nation_id": nation.id,
                }

                self.find_or_create_record(
                    Team,
                    {"name": team_data["Squad"], "gender": team_data["Gender"]},
                    team_dict,
                    f"team: {team_data['Squad']}",
                )
