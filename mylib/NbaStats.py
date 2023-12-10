import numpy as np
from nba_api.stats.static import teams  # players
from nba_api.stats.endpoints import teamgamelog  # shotchartdetail
from scipy.stats import norm, skew, kurtosis
import pandas as pd
from requests.exceptions import ReadTimeout
from time import sleep
from Support.Emailer import Emailer
from BasketballReferenceLinks import BasketBallReferenceLinks
from datetime import datetime, timedelta
import calendar


def get_team_id(teams_dictionary, team_):
    return teams_dictionary.loc[teams_dictionary.abbreviation == team_]["id"].iloc[0]


def get_all_games_current_season(season_start_date, season_end_date):
    stat_link = BasketBallReferenceLinks().all_games_in_month
    season_start_date = season_start_date.split("-")
    season_end_date = season_end_date.split("-")
    sty = int(season_start_date[0])
    stm = int(season_start_date[1])
    std = int(season_start_date[2])
    ey = int(season_end_date[0])
    em = int(season_end_date[1])
    ed = int(season_end_date[2])

    start_dt = datetime(year=sty, month=stm, day=std)
    end_dt = datetime(year=ey, month=em, day=ed)

    month_dict = {
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

    cur_dt = start_dt
    if cur_dt.month > 9:
        year_ = cur_dt.year + 1
    else:
        year_ = cur_dt.year
    df = pd.DataFrame()
    while cur_dt <= end_dt:
        link = stat_link.format(year=year_, month=month_dict[cur_dt.month].lower())
        df = pd.concat([df, pd.read_html(link)[0]])
        days_in_month = calendar.monthrange(year_, cur_dt.month)[1]
        cur_dt += timedelta(days_in_month)

    df["Date"] = pd.to_datetime(df["Date"])

    return df


def get_team_game_log(team_id, season, season_type):
    season_type.reverse()
    df = pd.concat(
        [
            teamgamelog.TeamGameLog(
                season=season, season_type_all_star=[s_], team_id=team_id
            ).get_data_frames()[0]
            for s_ in season_type
        ]
    )
    # df = log.get_data_frames()[0]
    df["opp"] = df.MATCHUP.apply(lambda r: r.split(" ")[-1])

    return df


def get_team_log_vs_opp(team_full_df, team_2_):
    return team_full_df.loc[team_full_df.opp == team_2_]


def get_vs_points(team_1_df, team_2_df):
    df_1 = team_1_df.reset_index(drop=True)
    df_2 = team_2_df.reset_index(drop=True)

    df = pd.concat(
        [df_1[["GAME_DATE", "MATCHUP", "WL", "PTS"]], df_2[["WL", "PTS"]]], axis=1
    )
    df.columns = ["GAME_DATE", "MATCHUP", "WL_1", "PTS_1", "WL_2", "PTS_2"]
    df["PTS_DIFF"] = abs(df["PTS_1"] - df["PTS_2"])

    return df


def get_pts_stats(df, last_n_games=1000, mode=1):
    df = df.iloc[:last_n_games, :]

    if mode == 1:
        mean = df.PTS.mean()
        stdv = df.PTS.std()
        median = df.PTS.median()
        skew_ = skew(df.PTS.values, axis=0, bias=True)
        kurtosis_ = kurtosis(df.PTS.values, axis=0, bias=True)

        return {
            "mean": mean,
            "std": stdv,
            "median": median,
            "skew": skew_,
            "kurtosis": kurtosis_,
        }
    else:
        mean_1 = df.PTS_1.mean()
        stdv_1 = df.PTS_1.std()
        median_1 = df.PTS_1.median()
        skew_1 = skew(df.PTS_1.values, axis=0, bias=True)
        kurtosis_1 = kurtosis(df.PTS_1.values, axis=0, bias=True)
        mean_2 = df.PTS_2.mean()
        stdv_2 = df.PTS_2.std()
        median_2 = df.PTS_2.median()
        skew_2 = skew(df.PTS_2.values, axis=0, bias=True)
        kurtosis_2 = kurtosis(df.PTS_2.values, axis=0, bias=True)
        mean_3 = df.PTS_DIFF.mean()
        stdv_3 = df.PTS_DIFF.std()
        median_3 = df.PTS_DIFF.median()

        return {
            "mean_1": mean_1,
            "std_1": stdv_1,
            "median_1": median_1,
            "mean_2": mean_2,
            "std_2": stdv_2,
            "median_2": median_2,
            "mean_diff": mean_3,
            "std_diff": stdv_3,
            "median_diff": median_3,
            "skew_1": skew_1,
            "kurtosis": kurtosis_1,
            "skew_2": skew_2,
            "kurtosis_2": kurtosis_2,
        }


def team_ranker(
    team_df,
    season,
    season_type,
    team_dict,
    mode=0,
    max_date=datetime(year=2050, month=1, day=1),
):
    cols = [
        "W_PCT",
        "FG_PCT",
        "FG3_PCT",
        "FTA",
        "FT_PCT",
        "OREB",
        "DREB",
        "AST",
        "STL",
        "BLK",
        "TOV",
        "PTS",
    ]
    metric_wights = [5, 1, 1, 0.5, 0.5, 2, 2, 1.5, 1.5, 1.5, 2, 1]
    res = pd.DataFrame()
    index_ = []
    team_log_dict = {}
    for team_id in team_df.id.values:
        run = True
        while run:
            try:
                team_name = team_df.loc[team_df.id == team_id]["abbreviation"].iloc[0]
                print(team_name)
                if mode == 0:
                    df = get_team_game_log(team_id, season, season_type)
                    team_log_dict[team_name] = df
                    df = df[cols]
                else:
                    df = team_dict[team_name]
                    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
                    df = df.loc[df["GAME_DATE"] <= max_date]

                df = df.mean()
                res = pd.concat([res, df], axis=1)
                index_.append(team_name)
                run = False
            except ReadTimeout:
                sleep(60)

    res.columns = index_
    easter_teams = [
        "MIA",
        "MIL",
        "BOS",
        "PHI",
        "TOR",
        "CHI",
        "BKN",
        "CLE",
        "ATL",
        "CHA",
        "NYK",
        "WAS",
        "IND",
        "DET",
        "ORL",
    ]
    western_teams = [
        "PHX",
        "MEM",
        "GSW",
        "DAL",
        "UTA",
        "DEN",
        "MIN",
        "LAC",
        "NOP",
        "SAS",
        "LAL",
        "SAC",
        "POR",
        "OKC",
        "HOU",
    ]
    easter_teams = res[easter_teams]
    western_teams = res[western_teams]

    easter_teams = (
        easter_teams.div(easter_teams.max(axis=1), axis=0)
        .multiply(metric_wights, axis=0)
        .sum()
    )
    easter_teams = (easter_teams / easter_teams.abs().max()) * 100 * 0.98

    western_teams = (
        western_teams.div(western_teams.max(axis=1), axis=0)
        .multiply(metric_wights, axis=0)
        .sum()
    )
    western_teams = (western_teams / western_teams.abs().max()) * 100 * 0.98

    return easter_teams, western_teams, team_log_dict


def get_stats(
    team_1, team_2, team_log_dict_, to_merge_df, alternate_source, team_names
):
    team_1_log = team_log_dict_[team_1]
    team_2_log = team_log_dict_[team_2]
    team_1_log = team_1_log.merge(
        to_merge_df, left_on="opp", right_on="index", how="left"
    )
    team_2_log = team_2_log.merge(
        to_merge_df, left_on="opp", right_on="index", how="left"
    )
    team_1_opp = get_team_log_vs_opp(team_1_log, team_2)
    team_2_opp = get_team_log_vs_opp(team_2_log, team_1)
    team_1_log["PTS"] = (team_1_log["PTS"] * team_1_log[0]) / 100
    team_2_log["PTS"] = (team_2_log["PTS"] * team_2_log[0]) / 100
    vs_df = get_vs_points(team_1_opp, team_2_opp)

    team_1_full_name = team_names.loc[team_names.abbreviation == team_1].full_name.iloc[
        0
    ]
    team_2_full_name = team_names.loc[team_names.abbreviation == team_2].full_name.iloc[
        0
    ]
    vs_df_2 = alternate_source.loc[
        (
            (alternate_source["Visitor/Neutral"] == team_1_full_name)
            & (alternate_source["Home/Neutral"] == team_2_full_name)
        )
        | (
            (alternate_source["Visitor/Neutral"] == team_2_full_name)
            & (alternate_source["Home/Neutral"] == team_1_full_name)
        )
    ]

    try:
        vs_df_2 = vs_df_2.rename(columns={"Date": "GAME_DATE"})
        vs_df_2["PTS_1"] = vs_df_2.apply(
            lambda r: r["PTS.1"] if r["Home/Neutral"] == team_1_full_name else r["PTS"],
            axis=1,
        )
        vs_df_2["PTS_2"] = vs_df_2.apply(
            lambda r: r["PTS.1"] if r["Home/Neutral"] == team_2_full_name else r["PTS"],
            axis=1,
        )
        vs_df_2["PTS_DIFF"] = vs_df_2["PTS_1"] - vs_df_2["PTS_2"]
        vs_df_2["WL_1"] = vs_df_2.apply(
            lambda r: "W" if r["PTS_DIFF"] > 0 else "L", axis=1
        )
        vs_df_2["WL_2"] = vs_df_2.apply(
            lambda r: "W" if r["PTS_DIFF"] < 0 else "L", axis=1
        )
        vs_df_2["PTS_DIFF"] = vs_df_2["PTS_DIFF"].abs()
        vs_df_2["GAME_DATE"] = pd.to_datetime(vs_df_2.GAME_DATE)
        vs_df["GAME_DATE"] = pd.to_datetime(vs_df.GAME_DATE)
        vs_df_2["MATCHUP"] = vs_df_2["Visitor/Neutral"] + "@" + vs_df_2["Home/Neutral"]
        vs_df_2 = vs_df_2.loc[~vs_df_2.GAME_DATE.isin(vs_df.GAME_DATE.values)][
            vs_df_2["PTS"].notna()
        ]
        vs_df_2 = vs_df_2.sort_values(by="GAME_DATE", ascending=False)

        vs_df = pd.concat([vs_df_2[vs_df.columns.values], vs_df], axis=0)
        vs_pts_stats = get_pts_stats(vs_df, mode=2)

        dm = vs_pts_stats["mean_diff"]
        ds = vs_pts_stats["std_diff"]
        win_margin_vs = [
            dm - (3 * ds),
            dm - (2 * ds),
            dm - (1 * ds),
            dm,
            dm + (1 * ds),
            dm + (2 * ds),
            dm + (3 * ds),
        ]

        dm = vs_pts_stats["mean_1"] + vs_pts_stats["mean_2"]
        ds = vs_pts_stats["std_1"] + vs_pts_stats["std_2"]
        total_points_vs = [
            dm - (3 * ds),
            dm - (2 * ds),
            dm - (1 * ds),
            dm,
            dm + (1 * ds),
            dm + (2 * ds),
            dm + (3 * ds),
        ]
    except ValueError:
        win_margin_vs = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
        total_points_vs = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
        vs_pts_stats = pd.DataFrame()

    print(team_1_log["PTS"].dtype)
    print(team_1_log["PTS"].dtype)

    team_1_log["PTS"] = pd.to_numeric(team_1_log["PTS"], errors="coerce")
    team_2_log["PTS"] = pd.to_numeric(team_2_log["PTS"], errors="coerce")
    team_1_pts_stats = get_pts_stats(team_1_log)
    team_2_pts_stats = get_pts_stats(team_2_log)
    team_1_pts_stats_last_5 = get_pts_stats(team_1_log, last_n_games=5)
    team_2_pts_stats_last_5 = get_pts_stats(team_2_log, last_n_games=5)
    team_1_pts_stats_last_10 = get_pts_stats(team_1_log, last_n_games=10)
    team_2_pts_stats_last_10 = get_pts_stats(team_2_log, last_n_games=10)
    team_1_pts_stats_last_15 = get_pts_stats(team_1_log, last_n_games=15)
    team_2_pts_stats_last_15 = get_pts_stats(team_2_log, last_n_games=15)

    dm = team_1_pts_stats_last_5["mean"] + team_2_pts_stats_last_5["mean"]
    ds = team_1_pts_stats_last_5["std"] + team_2_pts_stats_last_5["std"]
    total_points_lst_5 = [
        dm - (3 * ds),
        dm - (2 * ds),
        dm - (1 * ds),
        dm,
        dm + (1 * ds),
        dm + (2 * ds),
        dm + (3 * ds),
    ]

    dm = team_1_pts_stats_last_10["mean"] + team_2_pts_stats_last_10["mean"]
    ds = team_1_pts_stats_last_10["std"] + team_2_pts_stats_last_10["std"]
    total_points_lst_10 = [
        dm - (3 * ds),
        dm - (2 * ds),
        dm - (1 * ds),
        dm,
        dm + (1 * ds),
        dm + (2 * ds),
        dm + (3 * ds),
    ]

    dm = team_1_pts_stats_last_15["mean"] + team_2_pts_stats_last_15["mean"]
    ds = team_1_pts_stats_last_15["std"] + team_2_pts_stats_last_15["std"]
    total_points_lst_15 = [
        dm - (3 * ds),
        dm - (2 * ds),
        dm - (1 * ds),
        dm,
        dm + (1 * ds),
        dm + (2 * ds),
        dm + (3 * ds),
    ]

    dm = team_1_pts_stats["mean"] + team_2_pts_stats["mean"]
    ds = team_1_pts_stats["std"] + team_2_pts_stats["std"]
    total_points = [
        dm - (3 * ds),
        dm - (2 * ds),
        dm - (1 * ds),
        dm,
        dm + (1 * ds),
        dm + (2 * ds),
        dm + (3 * ds),
    ]

    index = ["-3sigma", "-2sigma", "-1sigma", "mean", "+1sigma", "+2sigma", "+3sigma"]

    d_ = {
        "win_margin_vs": win_margin_vs,
        "total_points_vs": total_points_vs,
        "total_points_l_5": total_points_lst_5,
        "total_points_l_10": total_points_lst_10,
        "total_points_l_15": total_points_lst_15,
        "total_points_ssn": total_points,
    }

    stats = pd.DataFrame(d_, index=index)
    return (
        stats,
        vs_df,
        vs_pts_stats,
        team_1_log,
        team_2_log,
        team_1_pts_stats,
        team_1_pts_stats_last_15,
        team_1_pts_stats_last_10,
        team_1_pts_stats_last_5,
        team_2_pts_stats,
        team_2_pts_stats_last_15,
        team_2_pts_stats_last_10,
        team_2_pts_stats_last_5,
    )


def get_games_on_date(
    games_df: pd.DataFrame, date: datetime, abbreviation_df: pd.DataFrame
):
    """Gets games on a provided date, from a basketball reference style games df"""
    df = games_df.loc[games_df["Date"] == date]
    df = df[["Visitor/Neutral", "Home/Neutral"]]
    df = df.merge(abbreviation_df, left_on="Visitor/Neutral", right_on="full_name")
    df = df.merge(abbreviation_df, left_on="Home/Neutral", right_on="full_name")

    return [list(i) for i in zip(df.abbreviation_x, df.abbreviation_y)]


if __name__ == "__main__":
    basketball_ref_games = get_all_games_current_season("2022-10-01", "2023-3-30")
    seaso_n_ = "2022-23"
    season__type_ = ["Regular Season", "Playoffs"]

    mailer_agent = Emailer()

    teams_ = teams.get_teams()
    teams__df = pd.DataFrame.from_dict(teams_)
    team_abbreviation = teams__df[["full_name", "abbreviation"]]

    easter__teams_, western__teams_, team__log_dict_ = team_ranker(
        teams__df, seaso_n_, season__type_, {}
    )

    to_merge__df = pd.concat([easter__teams_, western__teams_])
    to_merge__df = (to_merge__df / 98) * 100
    to_merge__df = to_merge__df.reset_index()
    games = get_games_on_date(
        games_df=basketball_ref_games,
        date=datetime(year=2023, month=3, day=25),
        abbreviation_df=team_abbreviation,
    )
    resy = []
    for game in games:
        team__1 = game[0]
        team__2 = game[1]
        team_1__id = get_team_id(teams__df, team__1)
        team_2__id = get_team_id(teams__df, team__2)

        (
            sts,
            vdf,
            vps,
            t1,
            t2,
            t1ps,
            t1p15,
            t1p10,
            t1p5,
            t2ps,
            t2p15,
            t2p10,
            t2p5,
        ) = get_stats(
            team__1,
            team__2,
            team__log_dict_,
            to_merge__df,
            basketball_ref_games,
            teams__df,
        )

        # Create a DataFrame with the data
        data = {
            "Last head to head dates": vdf.GAME_DATE.values,
            f"Last {team__1} head to head w/L": vdf.WL_1.values,
            "Last head to head point differences": vdf.PTS_DIFF.values,
            "Last head to head point differences skew": skew(
                vdf.PTS_DIFF.values, axis=0, bias=True
            ),
            "Lst head to head point differences kurtosis": kurtosis(
                vdf.PTS_DIFF.values, axis=0, bias=True
            ),
            "last_head_to_head_stats": vps,
        }

        emailer = ""
        emailer += f"<p>Last head to head dates: {vdf.GAME_DATE.values} \n</p>"
        emailer += f"<p>Last {team__1} head to head w/L: {vdf.WL_1.values}\n</p>"
        emailer += (
            f"<p>Last head to head point differences: {vdf.PTS_DIFF.values} \n</p>"
        )
        emailer += f"<p>Last head to head point differences skew: {skew(vdf.PTS_DIFF.values, axis=0, bias=True)} \n</p>"
        s = f"<p>Lst head to head point differences kurtosis: {kurtosis(vdf.PTS_DIFF.values, axis=0, bias=True)} \n</p>"
        emailer += s
        emailer += f"<p>Last head to head point differences: {vps} \n</p>"
        emailer += f"<p>*******************************************************************************************</p>"

        a = t1ps["mean"]
        b = t1ps["std"]
        c = t1ps["skew"]
        d = t1ps["kurtosis"]
        s = f"<p>{team__1} Season pts scaled mean: {a:.2f}  sdev: {b:.2f}  skew {c:.2f}  kurtosis {d:.2f}\n</p>"
        emailer += s
        data[f"{team__1} Season pts scaled mean"] = {
            "mean": a,
            "stdev": b,
            "skew": c,
            "kurtosis": d,
        }

        a = t1p15["mean"]
        b = t1p15["std"]
        c = t1p15["skew"]
        d = t1p15["kurtosis"]
        s = f"<p>{team__1} Last 15 pts scaled mean: {a:.2f}  sdev: {b:.2f}  skew {c:.2f}  kurtosis {d:.2f}\n</p>"
        emailer += s
        data[f"{team__1} Last 15 pts scaled mean"] = {
            "mean": a,
            "stdev": b,
            "skew": c,
            "kurtosis": d,
        }

        a = t1p10["mean"]
        b = t1p10["std"]
        c = t1p10["skew"]
        d = t1p10["kurtosis"]
        s = f"<p>{team__1} Last 10 pts scaled mean: {a:.2f}  sdev: {b:.2f}  skew {c:.2f}  kurtosis {d:.2f}\n</p>"
        emailer += s
        data[f"{team__1} Last 10 pts scaled mean"] = {
            "mean": a,
            "stdev": b,
            "skew": c,
            "kurtosis": d,
        }

        a = t1p5["mean"]
        b = t1p5["std"]
        c = t1p5["skew"]
        d = t1p5["kurtosis"]
        s = f"<p>{team__1} Last 5 pts scaled mean: {a:.2f}  sdev: {b:.2f}  skew {c:.2f}  kurtosis {d:.2f}\n</p>"
        emailer += s
        emailer += f"<p>*******************************************************************************************</p>"
        data[f"{team__1} Last 5 pts scaled mean"] = {
            "mean": a,
            "stdev": b,
            "skew": c,
            "kurtosis": d,
        }

        a = t2ps["mean"]
        b = t2ps["std"]
        c = t2ps["skew"]
        d = t2ps["kurtosis"]
        s = f"<p>{team__2} Season pts scaled mean: {a:.2f}  sdev: {b:.2f}  skew {c:.2f}  kurtosis {d:.2f}\n</p>"
        emailer += s
        data[f"{team__2} Season pts scaled mean"] = {
            "mean": a,
            "stdev": b,
            "skew": c,
            "kurtosis": d,
        }

        a = t2p15["mean"]
        b = t2p15["std"]
        c = t2p15["skew"]
        d = t2p15["kurtosis"]
        s = f"<p>{team__2} Last 15 pts scaled mean: {a:.2f}  sdev: {b:.2f}  skew {c:.2f}  kurtosis {d:.2f}\n</p>"
        emailer += s
        data[f"{team__2} Last 15 pts scaled mean"] = {
            "mean": a,
            "stdev": b,
            "skew": c,
            "kurtosis": d,
        }

        a = t2p10["mean"]
        b = t2p10["std"]
        c = t2p10["skew"]
        d = t2p10["kurtosis"]
        s = f"<p>{team__2} Last 10 pts scaled mean: {a:.2f}  sdev: {b:.2f}  skew {c:.2f}  kurtosis {d:.2f}\n</p>"
        emailer += s
        data[f"{team__2} Last 10 pts scaled mean"] = {
            "mean": a,
            "stdev": b,
            "skew": c,
            "kurtosis": d,
        }

        a = t2p5["mean"]
        b = t2p5["std"]
        c = t2p5["skew"]
        d = t2p5["kurtosis"]
        s = f"<p>{team__2} Last 5 pts scaled mean: {a:.2f}  sdev: {b:.2f}  skew {c:.2f}  kurtosis {d:.2f}\n</p>"
        emailer += s
        data[f"{team__2} Last 5 pts scaled mean"] = {
            "mean": a,
            "stdev": b,
            "skew": c,
            "kurtosis": d,
        }

        emailer += f"<p>*******************************************************************************************</p>"
        try:
            diff_cdf = norm.cdf(
                [i for i in range(41)], vps["mean_diff"], vps["std_diff"]
            )

            a = (diff_cdf[5] - diff_cdf[0]) * 100
            emailer += f"<p>Score Difference Probability 1 to 5: {a:.2f} \n</p>"
            b = (diff_cdf[10] - diff_cdf[5]) * 100
            emailer += f"<p>Score Difference Probability 6 to 10: {b:.2f} \n</p>"
            c = (diff_cdf[15] - diff_cdf[10]) * 100
            emailer += f"<p>Score Difference Probability 11 to 15: {c:.2f} \n</p>"
            d = (diff_cdf[20] - diff_cdf[15]) * 100
            emailer += f"<p>Score Difference Probability 16 to 20: {d:.2f} \n</p>"
            e = (diff_cdf[25] - diff_cdf[20]) * 100
            emailer += f"<p>Score Difference Probability 21 to 25: {e:.2f} \n</p>"
            f = (diff_cdf[30] - diff_cdf[25]) * 100
            emailer += f"<p>Score Difference Probability 26 to 30: {f:.2f} \n</p>"
            g = (diff_cdf[35] - diff_cdf[30]) * 100
            emailer += f"<p>Score Difference Probability 31 to 35: {g:.2f} \n</p>"
            h = (diff_cdf[40] - diff_cdf[35]) * 100
            emailer += f"<p>Score Difference Probability 36 to 40: {h:.2f} \n</p>"
            # noinspection PyTypedDict
            data["Score Difference Probability"] = {
                "1 to 5": a,
                "6 to 10": b,
                "11 to 15": c,
                "16 to 20": d,
                "21 to 25": e,
                "26 to 30": f,
                "31 to 35": g,
                "36 to 40": h,
            }
        except KeyError:
            emailer += f"<p>Score Difference Probability is not available.. \n</p>"
            data["Score Difference Probability"] = {
                "1 to 5": None,
                "6 to 10": None,
                "11 to 15": None,
                "16 to 20": None,
                "21 to 25": None,
                "26 to 30": None,
                "31 to 35": None,
                "36 to 40": None,
            }

        head_to_head_df = pd.DataFrame(
            {
                "Dates": data["Last head to head dates"],
                f"{team__1}_vs_{team__2}_wl": data[f"Last {team__1} head to head w/L"],
                "pts_diff": data["Last head to head point differences"],
            }
        )
        head_to_head_df["pts_diff_skew"] = None
        head_to_head_df["pts_diff_kurtosis"] = None
        head_to_head_df["pts_diff_skew"].iloc[-1] = data[
            "Last head to head point differences skew"
        ]
        head_to_head_df["pts_diff_kurtosis"].iloc[-1] = data[
            "Lst head to head point differences kurtosis"
        ]

        ii = "last_head_to_head_stats"
        head_to_head_stats_df = pd.DataFrame(
            {
                f"{team__1}": [
                    data[ii]["mean_1"],
                    data[ii]["std_1"],
                    data[ii]["median_1"],
                    data[ii]["skew_1"],
                    data[ii]["kurtosis"],
                ],
                f"{team__2}": [
                    data[ii]["mean_2"],
                    data[ii]["std_2"],
                    data[ii]["median_2"],
                    data[ii]["skew_2"],
                    data[ii]["kurtosis_2"],
                ],
            },
            index=["mean", "std", "median", "skew", "kurtosis"],
        )

        scaled_points_stats_df = pd.DataFrame(
            [
                data[f"{team__1} Season pts scaled mean"],
                data[f"{team__2} Season pts scaled mean"],
                data[f"{team__1} Last 15 pts scaled mean"],
                data[f"{team__2} Last 15 pts scaled mean"],
                data[f"{team__1} Last 10 pts scaled mean"],
                data[f"{team__2} Last 10 pts scaled mean"],
                data[f"{team__1} Last 5 pts scaled mean"],
                data[f"{team__2} Last 5 pts scaled mean"],
            ]
        ).T

        scaled_points_stats_df.columns = [
            f"{team__1}_season",
            f"{team__2}_season",
            f"{team__1}_last_15",
            f"{team__2}_last_15",
            f"{team__1}_last_10",
            f"{team__2}_last_10",
            f"{team__1}_last_5",
            f"{team__2}_last_5",
        ]

        score_diff_probability_df = pd.DataFrame(
            data["Score Difference Probability"], index=["probability"]
        ).T
        resy.append(
            {
                "head_to_head_df": head_to_head_df,
                "head_to_head_stats_df": head_to_head_stats_df,
                "scaled_points_stats_df": scaled_points_stats_df,
                "score_diff_probability_df": score_diff_probability_df,
            }
        )

        print(21)
    pass
