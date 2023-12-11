import requests
from databricks import sql
import time


# Function to start the cluster
def start_cluster(cluster_id, databricks_token):
    url = f"https://adb-8637293818359439.19.azuredatabricks.net/api/2.0/clusters/start"
    headers = {"Authorization": f"Bearer {databricks_token}"}
    payload = {"cluster_id": cluster_id}
    response = requests.post(url, headers=headers, json=payload)
    return response.ok


# Function to check the cluster state
def check_cluster_state(cluster_id, databricks_token):
    url = f"https://adb-8637293818359439.19.azuredatabricks.net/api/2.0/clusters/get"
    headers = {"Authorization": f"Bearer {databricks_token}"}
    payload = {"cluster_id": cluster_id}
    response = requests.get(url, headers=headers, json=payload)
    if response.ok:
        return response.json()["state"]
    return None


# Main logic
cluster_id = "1108-035620-j64ytjqr"
databricks_token = "<dapi3bef43da41746c4d496d4fcf22fd2f7e-3>"
# Start the cluster
if start_cluster(cluster_id, databricks_token):
    # Polling to check if the cluster is up
    while True:
        state = check_cluster_state(cluster_id, databricks_token)
        if state == "RUNNING":
            break
        time.sleep(10)


def execute_query(query):
    print("Querying data...")
    with sql.connect(
        server_hostname="adb-8637293818359439.19.azuredatabricks.net",
        http_path="sql/protocolv1/o/8637293818359439/1108-035620-j64ytjqr",
        access_token="dapi3bef43da41746c4d496d4fcf22fd2f7e-3",
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])
            return df


import pandas as pd
import sql
from databricks import sql

team__log_dict_ = {}

team__log_dict_["ATL"] = execute_query("select * from ATL")
team__log_dict_["BKN"] = execute_query("select * from BKN")
team__log_dict_["BOS"] = execute_query("select * from BOS")
team__log_dict_["CHA"] = execute_query("select * from CHA")
team__log_dict_["CHI"] = execute_query("select * from CHI")
team__log_dict_["CLE"] = execute_query("select * from CLE")
team__log_dict_["DAL"] = execute_query("select * from DAL")
team__log_dict_["DEN"] = execute_query("select * from DEN")
team__log_dict_["DET"] = execute_query("select * from DET")
team__log_dict_["GSW"] = execute_query("select * from GSW")
team__log_dict_["HOU"] = execute_query("select * from HOU")
team__log_dict_["IND"] = execute_query("select * from IND")
team__log_dict_["LAC"] = execute_query("select * from LAC")
team__log_dict_["LAL"] = execute_query("select * from LAL")
team__log_dict_["MEM"] = execute_query("select * from MEM")
team__log_dict_["MIA"] = execute_query("select * from MIA")
team__log_dict_["MIL"] = execute_query("select * from MIL")
team__log_dict_["MIN"] = execute_query("select * from MIN")
team__log_dict_["NOP"] = execute_query("select * from NOP")
team__log_dict_["NYK"] = execute_query("select * from NYK")
team__log_dict_["OKC"] = execute_query("select * from OKC")
team__log_dict_["ORL"] = execute_query("select * from ORL")
team__log_dict_["PHI"] = execute_query("select * from PHI")
team__log_dict_["PHX"] = execute_query("select * from PHX")
team__log_dict_["POR"] = execute_query("select * from POR")
team__log_dict_["SAC"] = execute_query("select * from SAC")
team__log_dict_["SAS"] = execute_query("select * from SAS")
team__log_dict_["TOR"] = execute_query("select * from TOR")
team__log_dict_["UTA"] = execute_query("select * from UTA")
team__log_dict_["WAS"] = execute_query("select * from WAS")

for key in team__log_dict_.keys():
    team__log_dict_[key] = team__log_dict_[key].drop("_c0", axis=1)


basketball_ref_games = execute_query("select * from basketball_ref_games")

easter__teams_ = execute_query("select * from easter__teams_")
western__teams_ = execute_query("select * from western__teams_")

easter__teams_ = easter__teams_.rename(columns={"team": "index"})
easter__teams_.index = easter__teams_["index"]
easter__teams_ = pd.Series(easter__teams_["rating"])
# easter__teams_ = easter__teams_["rating"]

western__teams_ = western__teams_.rename(columns={"team": "index"})
western__teams_.index = western__teams_["index"]
western__teams_ = pd.Series(western__teams_["rating"])
# western__teams_ = western__teams_["rating"]

team_abbreviation = execute_query("select * from team_abbreviation")

to_merge__df = execute_query("select * from to_merge__df")

to_merge__df = to_merge__df.rename(columns={"team": "index"})
to_merge__df = to_merge__df.rename(columns={"rating": 0})

games = execute_query("select * from games")

teams__df = execute_query("select * from teams__df")

g = []
for i in games["game"]:
    g.append([i])
games = g

new_list = [team[0].split("-") for team in games]

games = new_list

to_merge__df = to_merge__df.drop("_c0", axis=1)

for key in team__log_dict_.keys():
    team__log_dict_[key]["PTS"] = team__log_dict_[key]["PTS"].astype(int)
    # team__log_dict_[key]["FGM"] = team__log_dict_[key]["FGM"].astype(int)
    # team__log_dict_[key]["FGA"] = team__log_dict_[key]["FGA"].astype(int)
    # team__log_dict_[key]["FG%"] = team__log_dict_[key]["FG%"].astype(float)
    # team__log_dict_[key]["3PM"] = team__log_dict_[key]["3PM"].astype(int)
    # team__log_dict_[key]["3PA"] = team__log_dict_[key]["3PA"].astype(int)
    # team__log_dict_[key]["3P%"] = team__log_dict_[key]["3P%"].astype(float)
    # team__log_dict_[key]["FTM"] = team__log_dict_[key]["FTM"].astype(int)
    # team__log_dict_[key]["FTA"] = team__log_dict_[key]["FTA"].astype(int)
    # team__log_dict_[key]["FT%"] = team__log_dict_[key]["FT%"].astype(float)
    # team__log_dict_[key]["OREB"] = team__log_dict_[key]["OREB"].astype(int)
    # team__log_dict_[key]["DREB"] = team__log_dict_[key]["DREB"].astype(int)
    # team__log_dict_[key]["REB"] = team__log_dict_[key]["REB"].astype(int)
    # team__log_dict_[key]["AST"] = team__log_dict_[key]["AST"].astype(int)
    # team__log_dict_[key]["TOV"] = team__log_dict_[key]["TOV"].astype(int)


def load_data():
    return (
        teams__df,
        easter__teams_,
        western__teams_,
        team__log_dict_,
        to_merge__df,
        games,
        basketball_ref_games,
        team_abbreviation,
    )
