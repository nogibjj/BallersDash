from BasketballReferenceLinks import BasketBallReferenceLinks
from datetime import datetime, timedelta
import calendar
from requests import get
from bs4 import BeautifulSoup
import unicodedata
import unidecode
import requests
from bs4 import Comment
import pandas as pd


class Scraper:
    def __init__(self):
        self.month_dict = {
            1: "january",
            2: "february",
            3: "march",
            4: "april",
            5: "may",
            6: "june",
            7: "july",
            8: "august",
            9: "september",
            10: "october",
            11: "november",
            12: "december",
        }

    @staticmethod
    def date_formatter(dt):
        _date = dt.split("-")

        sty = int(_date[0])
        stm = int(_date[1])
        std = int(_date[2])

        return datetime(year=sty, month=stm, day=std)

    def get_all_games_current_season(self, season_start_date, season_end_date):
        stat_link = BasketBallReferenceLinks().all_games_in_month

        cur_dt = self.date_formatter(season_start_date)
        df = pd.DataFrame()
        while cur_dt <= self.date_formatter(season_end_date):
            link = stat_link.format(
                year=cur_dt.year, month=self.month_dict[cur_dt.month].lower()
            )
            df = pd.concat([df, pd.read_html(link)[0]])

            days_in_month = calendar.monthrange(cur_dt.year, cur_dt.month)[1]
            cur_dt += timedelta(days_in_month)

        return df

    @staticmethod
    def get_team_standings(year):
        stat_link = BasketBallReferenceLinks.team_standings.format(year=year)
        df = pd.read_html(stat_link)[0]

        return df

    @staticmethod
    def get_injury_report():
        stat_link = BasketBallReferenceLinks.injury_report
        df = pd.read_html(stat_link)[0]

        return df

    @staticmethod
    def get_player_points_total(year):
        stat_link = BasketBallReferenceLinks.player_point_totals.format(year=year)
        return pd.read_html(stat_link)[0]

    @staticmethod
    def get_player_per_game_stats(year):
        stat_link = BasketBallReferenceLinks.player_per_game_stats.format(year=year)
        return pd.read_html(stat_link)[0]

    @staticmethod
    def get_player_36_stats(year):
        stat_link = BasketBallReferenceLinks.player_per_36_stats.format(year=year)
        return pd.read_html(stat_link)[0]

    @staticmethod
    def get_player_100_stats(year):
        stat_link = BasketBallReferenceLinks.player_per_100_stats.format(year=year)
        return pd.read_html(stat_link)[0]

    @staticmethod
    def get_player_play_by_play_stats(year):
        stat_link = BasketBallReferenceLinks.player_play_by_play_stats.format(year=year)
        return pd.read_html(stat_link)[0]

    @staticmethod
    def get_player_advanced_stats(year):
        stat_link = BasketBallReferenceLinks.player_advanced_states.format(year=year)
        return pd.read_html(stat_link)[0]

    @staticmethod
    def get_player_shooting_stats(year):
        stat_link = BasketBallReferenceLinks.player_shooting.format(year=year)
        return pd.read_html(stat_link)[0]

    @staticmethod
    def get_player_adjusted_shooting_stats(year):
        stat_link = BasketBallReferenceLinks.player_adjusted_shooting.format(year=year)
        return pd.read_html(stat_link)[0]

    @staticmethod
    def get_team_ratings(year):
        stat_link = BasketBallReferenceLinks.team_ratings.format(year=year)
        return pd.read_html(stat_link)[0]

    @staticmethod
    def get_team_roster(year, team_abv):
        stat_link = BasketBallReferenceLinks.team_roster.format(
            year=year, team_abv=team_abv
        )
        return pd.read_html(stat_link)[0]

    def get_player_game_log(self, suffix__, year):
        stat_link = BasketBallReferenceLinks.player_game_log.format(
            suffix=suffix__, year=year, type="pgl_basic"
        )
        try:
            df = pd.read_html(stat_link)[7]
        except ValueError or IndexError:
            return pd.DataFrame()

        return self.get_second_table(df, stat_link, "pgl_basic_playoffs")

    @staticmethod
    def get_second_table(df, stat_link, id_):
        result = requests.get(stat_link).text
        data = BeautifulSoup(result, "html.parser")

        comments = data.find_all(string=lambda text: isinstance(text, Comment))

        try:
            for each in comments:
                if "table" in str(each):
                    df = pd.concat([df, pd.read_html(str(each), attrs={"id": id_})[0]])
                    break
        except ValueError:
            return df

        return df

    @staticmethod
    def create_last_name_part_of_suffix(potential_last_names):
        last_names = "".join(potential_last_names)
        if len(last_names) <= 5:
            return last_names[:].lower()
        else:
            return last_names[:5].lower()

    def get_player_suffix(self, name):
        short_cut = {
            "Clint Capela": r"/c/capelca01",
            "Enes Freedom": "/k/kanteen01",
            "C.J. Miles": "/m/milescj01",
            "Dennis Schröder": "/s/schrode01",
            "P.J. Washington": "/w/washipj01",
            "Nikola Vučević": "/v/vucevni01",
            "David Duke Jr.": "/d/dukeda01.",
            "Cedi Osman": "/o/osmande01",
            "Dāvis Bertāns": "/b/bertada01",
            "Luka Dončić": "/d/doncilu01",
            "Maxi Kleber": "/k/klebima01",
            "Frank Ntilikina": "/n/ntilila01",
            "Vlatko Čančar": "/c/cancavl01",
            "Nikola Jokić": "/j/jokicni01",
            "D.J. Augustin": "/a/augusdj01",
            "Alperen Şengün": "/s/sengual01",
            "T.J. McConnell": "/m/mccontj01",
            "P.J. Tucker": "/t/tuckepj01",
            "D'Angelo Russell": "/r/russeda01",
            "Didi Louzada": "/l/louzama01",
            "R.J. Hampton": "/h/hamptrj01",
            "B.J. Johnson": "/j/johnsbj01",
            "M.J. Walker": "/w/walkemj01",
            "D.J. Wilson": "/w/wilsodj01",
            "Royce O'Neale": "/o/onealro01",
        }

        if name in short_cut.keys():
            return f"/players{short_cut[name]}"

        normalized_name = unidecode.unidecode(
            unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode("utf-8")
        )

        other_names_search = []
        first_name_part = ""
        first_name = ""
        initial = ""
        last_name_part = ""

        if normalized_name == "Metta World Peace":
            suffix = "/players/a/artesro01.html"
        else:
            split_normalized_name = normalized_name.split(" ")
            if len(split_normalized_name) < 2:
                return None
            initial = normalized_name.split(" ")[1][0].lower()
            all_names = name.split(" ")
            first_name_part = unidecode.unidecode(all_names[0][:2].lower())
            first_name = all_names[0]
            other_names = all_names[1:]
            other_names_search = other_names
            last_name_part = self.create_last_name_part_of_suffix(other_names)
            suffix = (
                "/players/"
                + initial
                + "/"
                + last_name_part
                + first_name_part
                + "01.html"
            )
        player_r = get(f"https://www.basketball-reference.com{suffix}")
        while player_r.status_code == 404:
            other_names_search.pop(0)
            last_name_part = self.create_last_name_part_of_suffix(other_names_search)
            initial = last_name_part[0].lower()
            suffix = (
                "/players/"
                + initial
                + "/"
                + last_name_part
                + first_name_part
                + "01.html"
            )
            player_r = get(f"https://www.basketball-reference.com{suffix}")
        while player_r.status_code == 200:
            player_soup = BeautifulSoup(player_r.content, "html.parser")
            h1 = player_soup.find("h1")
            if h1:
                page_name = h1.find("span").text
                """
                    Test if the URL we constructed matches the 
                    name of the player on that page; if it does,
                    return suffix, if not add 1 to the numbering
                    and recheck.
                """
                if (unidecode.unidecode(page_name)).lower() == normalized_name.lower():
                    return suffix
                else:
                    page_names = unidecode.unidecode(page_name).lower().split(" ")
                    page_first_name = page_names[0]
                    if first_name.lower() == page_first_name.lower():
                        return suffix
                    # if players have same first two letters of last name then just
                    # increment suffix
                    elif first_name.lower()[:2] == page_first_name.lower()[:2]:
                        player_number = (
                            int("".join(c for c in suffix if c.isdigit())) + 1
                        )
                        if player_number < 10:
                            player_number = f"0{str(player_number)}"
                        suffix = f"/players/{initial}/{last_name_part}{first_name_part}{player_number}.html"
                    else:
                        other_names_search.pop(0)
                        last_name_part = self.create_last_name_part_of_suffix(
                            other_names_search
                        )
                        initial = last_name_part[0].lower()
                        suffix = (
                            "/players/"
                            + initial
                            + "/"
                            + last_name_part
                            + first_name_part
                            + "01.html"
                        )

                    player_r = get(f"https://www.basketball-reference.com{suffix}")

        return None


if __name__ == "__main__":
    bs_scraper = Scraper()

    team_roster = bs_scraper.get_team_roster("2023", "PHI")

    suffix_ = bs_scraper.get_player_suffix("James Harden").split(".")[0]
    player_game_log = bs_scraper.get_player_game_log(suffix_, "2022")

    injuries = bs_scraper.get_injury_report()
    player_per_game_stats = bs_scraper.get_player_per_game_stats("2022")
    player_per_36_stats = bs_scraper.get_player_36_stats("2022")
    player_per_100_stats = bs_scraper.get_player_100_stats("2022")
    player_play_by_play_stats = bs_scraper.get_player_play_by_play_stats("2022")
    player_advanced_stats = bs_scraper.get_player_advanced_stats("2022")
    player_shooting_stats = bs_scraper.get_player_shooting_stats("2022")
    team_ratings = bs_scraper.get_team_ratings("2022")
    all_games = bs_scraper.get_all_games_current_season("2022-01-02", "2022-04-01")
    team_standings = bs_scraper.get_team_standings("2022")
    player_points_total = bs_scraper.get_player_points_total("2022")

    print(21)
