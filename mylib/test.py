from NbaStats import *
from NbaStatsDash import *


seaso_n_ = '2023-24'
season__type_ = 'Regular Season'
today_ = '2023-10-17'
ss = '2023-10-17'
se = '2024-04-10'


teams__df, easter__teams_, western__teams_, team__log_dict_, to_merge__df, games, basketball_ref_games, \
        team_abbreviation = load_data(seaso_n_, season__type_, today_, ss, se)


print(teams__df)