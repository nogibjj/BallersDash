from NbaStats import *
from NbaStatsDash import *
from datetime import datetime


seaso_n_ = '2023-24'
season__type_ = ['Regular Season']
# date from string
today_ = '2023-10-17'
today_ = datetime.strptime(today_, '%Y-%m-%d')
ss = '2023-10-17'
# ss = datetime.strptime(ss, '%Y-%m-%d')
se = '2024-04-10'
# se = datetime.strptime(se, '%Y-%m-%d')


teams__df, easter__teams_, western__teams_, team__log_dict_, to_merge__df, games, basketball_ref_games, \
        team_abbreviation = load_data(seaso_n_, season__type_, today_, ss, se)


print(teams__df)