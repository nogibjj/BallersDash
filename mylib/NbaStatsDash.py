from NbaStats import *
import streamlit as st
from datetime import date
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, CrosshairTool, PanTool
from bokeh.layouts import column
from PIL import Image
from Support.scraper import Scraper


@st.cache_data
def load_data(seaso_n, season__type, toda_y, start, end):
    basketball_ref_games_ = get_all_games_current_season(str(start), str(end))
    teams__ = teams.get_teams()
    teams_df = pd.DataFrame.from_dict(teams__)
    team_abbreviation_ = teams_df[["full_name", "abbreviation"]]

    easter_teams_, western_teams_, team_log_dict_ = team_ranker(
        teams_df, seaso_n, season__type, {}
    )

    to_merge_df = pd.concat([easter_teams_, western_teams_])
    to_merge_df = (to_merge_df / 98) * 100
    to_merge_df = to_merge_df.reset_index()

    dd_ = datetime(year=toda_y.year, month=toda_y.month, day=toda_y.day)
    games_ = get_games_on_date(
        games_df=basketball_ref_games_, date=dd_, abbreviation_df=team_abbreviation_
    )

    return (
        teams_df,
        easter_teams_,
        western_teams_,
        team_log_dict_,
        to_merge_df,
        games_,
        basketball_ref_games_,
        team_abbreviation_,
    )


def h_2_h_stats_helper(dat, dict_, team_, id_):
    a_ = dat["mean"]
    b_ = dat["std"]
    c_ = dat["skew"]
    d_ = dat["kurtosis"]

    dict_[f"{team_} {id_}"] = {"mean": a_, "stdev": b_, "skew": c_, "kurtosis": d_}


def h_2_h_helper(
    all_scores_: list, m: float, s_: float, col: str, team_: str, pcdf, id_, p=0
):
    max_pts = m + s_  # mean + stddev
    min_pts = m - s_
    max_pcdf = max(pcdf)

    source = ColumnDataSource(data=dict(x=all_scores_, y=pcdf))
    if p == 0:
        p = figure(title=f"{id_}", x_axis_label="Points", y_axis_label="Probability")

    p.line("x", "y", source=source, line_width=2, line_color=col, legend_label=team_)
    p.line(
        x=[max_pts, max_pts],
        y=[0, max_pcdf],
        line_width=2,
        line_color=col,
        line_dash="dashed",
    )
    p.line(
        x=[min_pts, min_pts],
        y=[0, max_pcdf],
        line_width=2,
        line_color=col,
        line_dash="dashed",
    )
    hover = HoverTool(
        tooltips=[("Points", "@x"), ("Probability %", "@y{0.00}")], mode="vline"
    )
    p.add_tools(hover)

    return p


def h_2h_pdf_plot_helper(
    all_scores_: list, m: float, s_: float, col: str, team_: str, id_: str, p=0
) -> figure:
    pdf = [p * 100 for p in norm.pdf(all_scores_, m, s_)]
    return h_2_h_helper(all_scores_, m, s_, col, team_, pdf, id_, p)


def h_2h_cdf_plot_helper(
    all_scores_: list, m: float, s_: float, col: str, team_: str, id_: str, p=0
) -> figure:
    cdf = [p * 100 for p in norm.cdf(all_scores_, m, s_)]
    return h_2_h_helper(all_scores_, m, s_, col, team_, cdf, id_, p)


def scaled_plot_helper(m1_, s1_, m2_, s2_, all_scores_, team_1, team_2, id_):
    szn_team_1_graph = h_2h_pdf_plot_helper(
        all_scores_, m1_, s1_, "black", team_1, f"PDF {id_}"
    )
    szn_team_2_graph_pdf = h_2h_pdf_plot_helper(
        all_scores_, m2_, s2_, "red", team_2, f"PDF {id_}", szn_team_1_graph
    )
    szn_team_2_graph_pdf.legend.location = "top_left"

    crosshair_ = CrosshairTool(line_alpha=0.4, line_color="#1f77b4")
    szn_team_2_graph_pdf.add_tools(crosshair_)

    szn_team_1_graph = h_2h_cdf_plot_helper(
        all_scores_, m1_, s1_, "black", team_1, f"CDF {id_}"
    )
    szn_team_2_graph_cdf = h_2h_cdf_plot_helper(
        all_scores_, m2_, s2_, "red", team_2, f"CDF {id_}", szn_team_1_graph
    )
    szn_team_2_graph_cdf.legend.location = "top_left"
    szn_team_2_graph_cdf.add_tools(crosshair_)

    st.bokeh_chart(column(szn_team_2_graph_pdf, szn_team_2_graph_cdf))


def raw_plots_helper(t, team_, p, clr, mode=0, src_=None):
    if mode == 0:
        title = f"{team_} Raw Points"
        src = ColumnDataSource(
            data=dict(
                x=t["GAME_DATE"],
                y=t["PTS"],
                dt=t["GAME_DATE"].dt.strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
    else:
        title = team_
        src = ColumnDataSource(
            data=dict(
                x=t["GAME_DATE"],
                y=t[src_],
                dt=t["GAME_DATE"].dt.strftime("%Y-%m-%d %H:%M:%S"),
            )
        )

    x = p.line("x", "y", line_width=2, legend_label=title, line_color=clr, source=src)
    p.scatter("x", "y", line_width=4, line_color=clr, source=src)
    hov = HoverTool(
        mode="vline", tooltips=[("Date", "@dt}"), ("Points", "@y")], renderers=[x]
    )
    p.add_tools(hov)

    return p


# Define a function to apply styles to a DataFrame
def color_by_score(val):
    if val == "W":
        color = "green"
    else:
        color = "red"
    return f"background-color: {color}"


# Define a function to create a row-wise heatmap
def row_heatmap(row):
    # Normalize the row values to the range [0, 1]
    normed = (row - row.min()) / (row.max() - row.min())
    # Use seaborn's color map to create a color palette
    cmap = {
        0: "#D0F0C0",  # Green
        1: "#F8D030",  # Yellow
        2: "#F08030",  # Orange
        3: "#F0A0A0",  # Red
        4: "#C03028",  # Dark red
        5: "#A040A0",  # Purple
        6: "#A0C8F0",  # Blue
        7: "#6890F0",  # Light blue
    }
    # Map the normalized values to colors
    colors = normed.apply(lambda x: f"background-color: {cmap[int(round(x * 7))]}")
    # Return the CSS styles as a Series
    return colors


if __name__ == "__main__":
    today_ = date.today()
    bs_scraper = Scraper()

    st.set_page_config(layout="wide")
    st.title("NBA Stats Dashboard. By: Rakeen Rouf")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        season_year = st.text_input("Season Year", "2023-24")
        if len(season_year) != 7:
            st.text("Wrong input for Season Year")
            exit()
        if season_year[-3] != "-":
            st.text("Wrong input for Season Year")
            exit()
    with col2:
        ss = st.date_input("Start Day", date(2023, 10, 1))
    with col3:
        se = st.date_input("End Day", today_)
    with col4:
        options = st.multiselect(
            "Game Types", ["Regular Season", "Playoffs"], ["Regular Season", "Playoffs"]
        )

    seaso_n_ = season_year
    season__type_ = options

    (
        teams__df,
        easter__teams_,
        western__teams_,
        team__log_dict_,
        to_merge__df,
        games,
        basketball_ref_games,
        team_abbreviation,
    ) = load_data(seaso_n_, season__type_, today_, ss, se)

    for game in games:
        team__1 = game[0]
        team__2 = game[1]
        if st.checkbox(f"{team__1} VS {team__2}"):
            # Define the main tabs
            tabs = [
                "Injury Report",
                "score_diff_probability",
                "Head to Head",
                "scaled_points_stats",
                "Raw Stats",
            ]
            main_tab = st.radio("Select a tab", tabs)

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

            h_2_h_stats_helper(t1ps, data, team__1, "Season pts scaled mean")
            h_2_h_stats_helper(t1p15, data, team__1, "Last 15 pts scaled mean")
            h_2_h_stats_helper(t1p10, data, team__1, "Last 10 pts scaled mean")
            h_2_h_stats_helper(t1p5, data, team__1, "Last 5 pts scaled mean")
            h_2_h_stats_helper(t2ps, data, team__2, "Season pts scaled mean")
            h_2_h_stats_helper(t2p15, data, team__2, "Last 15 pts scaled mean")
            h_2_h_stats_helper(t2p10, data, team__2, "Last 10 pts scaled mean")
            h_2_h_stats_helper(t2p5, data, team__2, "Last 5 pts scaled mean")

            try:
                diff_cdf = norm.cdf(
                    [i for i in range(41)], vps["mean_diff"], vps["std_diff"]
                )

                a = (diff_cdf[5] - diff_cdf[0]) * 100
                b = (diff_cdf[10] - diff_cdf[5]) * 100
                c = (diff_cdf[15] - diff_cdf[10]) * 100
                d = (diff_cdf[20] - diff_cdf[15]) * 100
                e = (diff_cdf[25] - diff_cdf[20]) * 100
                f = (diff_cdf[30] - diff_cdf[25]) * 100
                g = (diff_cdf[35] - diff_cdf[30]) * 100
                h = (diff_cdf[40] - diff_cdf[35]) * 100
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
                    f"{team__1}_vs_{team__2}_wl": data[
                        f"Last {team__1} head to head w/L"
                    ],
                    "pts_diff": data["Last head to head point differences"],
                }
            )
            head_to_head_df["pts_diff_skew"] = None
            head_to_head_df["pts_diff_kurtosis"] = None
            head_to_head_df.iloc[-1]["pts_diff_skew"] = data[
                "Last head to head point differences skew"
            ]
            head_to_head_df.iloc[-1]["pts_diff_kurtosis"] = data[
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

            hist = [
                f"{team__1} Season pts scaled mean",
                f"{team__2} Season pts scaled mean",
                f"{team__1} Last 15 pts scaled mean",
                f"{team__2} Last 15 pts scaled mean",
                f"{team__1} Last 10 pts scaled mean",
                f"{team__2} Last 10 pts scaled mean",
                f"{team__1} Last 5 pts scaled mean",
                f"{team__2} Last 5 pts scaled mean",
            ]

            dict_holder = {"mean": None, "stdev": None, "skew": None, "kurtosis": None}
            data.update({key: dict_holder for key in set(hist) - set(data.keys())})

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

            st.subheader(f"{team__1} VS {team__2}")
            all_scores = list(range(50, 170))
            if main_tab == "Head to Head":
                st.text(f"Head to Head")
                col1, col2 = st.columns(2)
                with col1:
                    try:
                        st.dataframe(head_to_head_df)
                    except ValueError:
                        st.text("Head to Head data fame not available.")
                with col2:
                    try:
                        st.dataframe(head_to_head_stats_df)
                    except ValueError:
                        st.text("Head to Head stats data frame not available.")

                m1 = head_to_head_stats_df[team__1]["mean"]
                s1 = head_to_head_stats_df[team__1]["std"]
                m2 = head_to_head_stats_df[team__2]["mean"]
                s2 = head_to_head_stats_df[team__2]["std"]

                h_2_h_team_1_graph = h_2h_pdf_plot_helper(
                    all_scores, m1, s1, "black", team__1, "PDF"
                )
                h_2_h_team_2_graph_pdf = h_2h_pdf_plot_helper(
                    all_scores, m2, s2, "red", team__2, "PDF", h_2_h_team_1_graph
                )
                h_2_h_team_2_graph_pdf.legend.location = "top_left"

                crosshair = CrosshairTool(line_alpha=0.4, line_color="#1f77b4")
                h_2_h_team_2_graph_pdf.add_tools(crosshair)

                h_2_h_team_1_graph = h_2h_cdf_plot_helper(
                    all_scores, m1, s1, "black", team__1, "CDF"
                )
                h_2_h_team_2_graph_cdf = h_2h_cdf_plot_helper(
                    all_scores, m2, s2, "red", team__2, "CDF", h_2_h_team_1_graph
                )
                h_2_h_team_2_graph_cdf.legend.location = "top_left"
                h_2_h_team_2_graph_cdf.add_tools(crosshair)

                col1, col2 = st.columns(2)
                with col1:
                    try:
                        st.bokeh_chart(
                            column(h_2_h_team_2_graph_pdf, h_2_h_team_2_graph_cdf)
                        )
                    except ValueError:
                        st.text("Head to Head distribution plots not available.")

            vdf["GAME_DATE"] = pd.to_datetime(vdf["GAME_DATE"])
            vdf["dt"] = vdf["GAME_DATE"].dt.strftime("%Y-%m-%d %H:%M:%S")
            srcc = vdf

            pp0 = figure(
                title="Pts Diff",
                x_axis_label="Date",
                y_axis_label="Points",
                x_axis_type="datetime",
            )
            xx = pp0.line(
                "GAME_DATE",
                "PTS_DIFF",
                line_width=2,
                legend_label=f"PTS_DIFF",
                line_color="blue",
                source=srcc,
            )
            pp0.scatter(
                "GAME_DATE", "PTS_DIFF", line_width=4, line_color="blue", source=srcc
            )
            hov_ = HoverTool(
                mode="vline",
                tooltips=[("Date", "@dt}"), ("Points", "@PTS_DIFF")],
                renderers=[xx],
            )
            pp0.add_tools(hov_)

            pp = figure(
                title="Raw Pts",
                x_axis_label="Date",
                y_axis_label="Points",
                x_axis_type="datetime",
            )
            xx = pp.line(
                "GAME_DATE",
                "PTS_1",
                line_width=2,
                legend_label=f"PTS_{team__1}",
                line_color="black",
                source=srcc,
            )
            yy = pp.line(
                "GAME_DATE",
                "PTS_2",
                line_width=2,
                legend_label=f"PTS_{team__2}",
                line_color="red",
                source=srcc,
            )
            pp.scatter(
                "GAME_DATE", "PTS_1", line_width=4, line_color="black", source=srcc
            )
            pp.scatter(
                "GAME_DATE", "PTS_2", line_width=4, line_color="red", source=srcc
            )
            hov_ = HoverTool(
                mode="vline",
                tooltips=[
                    ("Date", "@dt}"),
                    (f"{team__1}", "@PTS_1"),
                    (f"{team__2}", "@PTS_2"),
                ],
                renderers=[xx, yy],
            )
            pp.add_tools(hov_)

            if main_tab == "scaled_points_stats":
                st.text(f"scaled_points_stats")
                try:
                    st.dataframe(scaled_points_stats_df)
                except ValueError:
                    st.text("Scaled Points stats data frame not available")

                t1["GAME_DATE"] = pd.to_datetime(t1["GAME_DATE"])
                t2["GAME_DATE"] = pd.to_datetime(t2["GAME_DATE"])

                pan = PanTool(dimensions="width")
                p_r = figure(
                    title=f"Season Points Scaled",
                    x_axis_label="Date",
                    y_axis_label="points",
                    x_axis_type="datetime",
                    plot_width=1000,
                    plot_height=600,
                    tools=[pan, "xwheel_zoom"],
                    active_scroll="xwheel_zoom",
                )
                p_r = raw_plots_helper(t1, team__1, p_r, "black")
                p_r = raw_plots_helper(t2, team__2, p_r, "red")

                try:
                    st.bokeh_chart(p_r)
                except ValueError:
                    st.text("raw scaled plots not available")

            if main_tab == "Head to Head":
                with col2:
                    try:
                        st.bokeh_chart(column(pp0, pp))
                    except ValueError:
                        st.text("Head to Head Diff anf Raw plots not available")
                col1, col2 = st.columns(2)

                with col1:
                    m1 = scaled_points_stats_df[f"{team__1}_season"]["mean"]
                    s1 = scaled_points_stats_df[f"{team__1}_season"]["stdev"]
                    m2 = scaled_points_stats_df[f"{team__2}_season"]["mean"]
                    s2 = scaled_points_stats_df[f"{team__2}_season"]["stdev"]
                    scaled_plot_helper(
                        m1, s1, m2, s2, all_scores, team__1, team__2, "All Season"
                    )

                    m1 = scaled_points_stats_df[f"{team__1}_last_10"]["mean"]
                    s1 = scaled_points_stats_df[f"{team__1}_last_10"]["stdev"]
                    m2 = scaled_points_stats_df[f"{team__2}_last_10"]["mean"]
                    s2 = scaled_points_stats_df[f"{team__2}_last_10"]["stdev"]
                    scaled_plot_helper(
                        m1, s1, m2, s2, all_scores, team__1, team__2, "Last 10 Games"
                    )

                with col2:
                    m1 = scaled_points_stats_df[f"{team__1}_last_15"]["mean"]
                    s1 = scaled_points_stats_df[f"{team__1}_last_15"]["stdev"]
                    m2 = scaled_points_stats_df[f"{team__2}_last_15"]["mean"]
                    s2 = scaled_points_stats_df[f"{team__2}_last_15"]["stdev"]
                    scaled_plot_helper(
                        m1, s1, m2, s2, all_scores, team__1, team__2, "Last 15 Games"
                    )

                    m1 = scaled_points_stats_df[f"{team__1}_last_5"]["mean"]
                    s1 = scaled_points_stats_df[f"{team__1}_last_5"]["stdev"]
                    m2 = scaled_points_stats_df[f"{team__2}_last_5"]["mean"]
                    s2 = scaled_points_stats_df[f"{team__2}_last_5"]["stdev"]
                    scaled_plot_helper(
                        m1, s1, m2, s2, all_scores, team__1, team__2, "Last 5 Games"
                    )

            if main_tab == "score_diff_probability":
                st.text(f"score_diff_probability")
                col1, col2 = st.columns(2)

                with col2:
                    try:
                        st.dataframe(
                            score_diff_probability_df.style.background_gradient(
                                cmap="YlGnBu"
                            )
                        )
                    except ValueError:
                        st.text("Score Diff Probability data frame not available")

                all_diffs = list(range(0, 50))
                m1 = score_diff_probability_df.mean()
                s1 = score_diff_probability_df.std()
                p_1 = h_2h_pdf_plot_helper(all_diffs, m1, s1, "black", "PDF", "PDF")
                p_2 = h_2h_cdf_plot_helper(all_diffs, m1, s1, "black", "CDF", "CDF")

                with col1:
                    try:
                        st.bokeh_chart(column(p_1, p_2))
                    except ValueError:
                        st.text("Score Diff Probability data frame not available")

            if main_tab == "Raw Stats":
                st.text("Raw Stats")
                t1 = team__log_dict_[team__1]
                t1["GAME_DATE"] = pd.to_datetime(t1["GAME_DATE"])
                t1 = t1.dropna(subset=["GAME_DATE"])
                t2 = team__log_dict_[team__2]
                t2["GAME_DATE"] = pd.to_datetime(t1["GAME_DATE"])
                t2 = t2.dropna(subset=["GAME_DATE"])

                pan = PanTool(dimensions="width")
                p_r = figure(
                    title=f"Season Points",
                    x_axis_label="Date",
                    y_axis_label="points",
                    x_axis_type="datetime",
                    plot_width=1000,
                    plot_height=600,
                    tools=[pan, "xwheel_zoom"],
                    active_scroll="xwheel_zoom",
                )
                p_r = raw_plots_helper(t1, team__1, p_r, "black")
                p_r = raw_plots_helper(t2, team__2, p_r, "red")

                try:
                    if st.checkbox(f"See detail game histories"):
                        st.caption(team__1)
                        t1s = t1.style.applymap(color_by_score, subset=["WL"])
                        t1s = t1s.background_gradient(cmap="YlGnBu")
                        st.dataframe(t1s)
                        st.caption(team__2)
                        t2s = t2.style.applymap(color_by_score, subset=["WL"])
                        t2s = t2s.background_gradient(cmap="YlGnBu")

                        st.dataframe(t2s)
                    st.bokeh_chart(p_r)

                    # Create a multiselect widget to allow the user to select columns
                    column2 = st.selectbox("Select column to plot", t2.columns)

                    pan_ = PanTool(dimensions="width")
                    f = figure(
                        title=f"{column2} Time series",
                        x_axis_label="DT",
                        y_axis_label=column2,
                        x_axis_type="datetime",
                        plot_width=1000,
                        plot_height=600,
                        tools=[pan_, "xwheel_zoom"],
                        active_scroll="xwheel_zoom",
                    )
                    f = raw_plots_helper(
                        t1, f"{team__1} {column2}", f, "black", 1, column2
                    )
                    f = raw_plots_helper(
                        t2, f"{team__2} {column2}", f, "red", 1, column2
                    )

                    st.bokeh_chart(f, use_container_width=True)

                except ValueError:
                    st.text("Raw data not available")

            if main_tab == "Injury Report":
                injury_report = bs_scraper.get_injury_report()
                teams = team_abbreviation.loc[
                    team_abbreviation["abbreviation"].isin([team__1, team__2])
                ]["full_name"]
                injury_report = injury_report.loc[
                    injury_report["Team"].isin(teams.values)
                ]
                st.dataframe(injury_report)

    try:
        # replace with images/illusion.jpg when deploying
        image = Image.open("../images/illusion.jpg")
        st.image(image, caption="Time is constant.")
    except FileNotFoundError:
        pass
