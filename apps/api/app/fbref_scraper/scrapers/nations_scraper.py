"""Nations scraper for FBRef data extraction."""

from app.models import Nation

from ..core import WebScraper, get_config


class NationsScraper(WebScraper):
    def scrape(self) -> None:
        """Scrape nation data."""
        config = get_config()
        url = f"{config.FBREF_BASE_URL}/en/countries/"
        self.load_page(url)
        df_list = self.fetch_html_table(url)

        for nation_tuple in df_list[0].iterrows():
            nation_data = nation_tuple[1]

            country_a_tag = self.find_element("a", string=nation_data["Country"])
            if not country_a_tag:
                continue

            country_tr = country_a_tag.find_parent("tr")

            href = country_a_tag["href"]
            country_code = self.extract_fbref_id(href)

            competitions_td = country_tr.find("td", {"data-stat": "competitions"})
            clubs_url = None
            if competitions_td.text.strip():
                clubs_a_tag = country_tr.find("td", {"data-stat": "club_count"}).find("a")
                if clubs_a_tag:
                    clubs_url = clubs_a_tag["href"]

            nation_data_dict = {
                "name": nation_data["Country"],
                "governing_body": nation_data["Governing Body"],
                "country_code": country_code,
                "fbref_url": country_a_tag["href"],
                "clubs_url": clubs_url,
            }

            self.find_or_create_record(
                Nation,
                {"name": nation_data["Country"]},
                nation_data_dict,
                f"nation: {nation_data['Country']}",
            )
