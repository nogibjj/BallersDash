class BasketBallReferenceLinks:
    all_games_in_month = r"https://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html#schedule"
    team_standings = r"https://www.basketball-reference.com/leagues/NBA_{year}_standings.html#expanded_standings"
    player_point_totals = r"https://www.basketball-reference.com/leagues/NBA_{year}_totals.html#totals_stats"
    player_per_game_stats = r"https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html#per_game_stats"
    player_per_36_stats = r"https://www.basketball-reference.com/leagues/NBA_{year}_per_minute.html#per_minute_stats"
    player_per_100_stats = r"https://www.basketball-reference.com/leagues/NBA_{year}_per_poss.html#per_poss_stats"
    player_advanced_states = r"https://www.basketball-reference.com/leagues/NBA_{year}_advanced.html#advanced_stats"
    player_play_by_play_stats = r"https://www.basketball-reference.com/leagues/NBA_{year}_play-by-play.html#pbp_stats"
    player_shooting = r"https://www.basketball-reference.com/leagues/NBA_{year}_shooting.html#shooting_stats"
    player_adjusted_shooting = r"https://www.basketball-reference.com/leagues/NBA_{year}_adj_shooting.html#adj-shooting"
    team_ratings = (
        r"https://www.basketball-reference.com/leagues/NBA_{year}_ratings.html#ratings"
    )
    player_game_log = (
        r"https://www.basketball-reference.com/{suffix}/gamelog/{year}#{type}"
    )
    team_roster = (
        r"https://www.basketball-reference.com/teams/{team_abv}/{year}.html#roster"
    )
    team_names = [
        "Atl",
        "Bos",
        "Brk",
        "Cho",
        "Chi",
        "Cle",
        "Dal",
        "Den",
        "Det",
        "Gsw",
        "Hou",
        "Ind",
        "LAC",
        "LAL",
        "Mem",
        "Mia",
        "Mil",
        "Min",
        "Nop",
        "Nyk",
        "Okc",
        "Orl",
        "Phi",
        "Pho",
        "Por",
        "Sac",
        "Sas",
        "Tor",
        "Uta",
        "Was",
    ]
    injury_report = r"https://www.basketball-reference.com/friv/injuries.fcgi#injuries"
