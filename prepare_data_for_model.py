import pandas as pd
import numpy as np
import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from data.process_game import *
from statsmodels.compat import lzip
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.formula.api import ols

## Team map
team_map = {
        'DEN': 'Denver',
        'LAL': 'LALakers',
        'SAS': 'SanAntonio',
        'DAL': 'Dallas',
        'BOS': 'Boston',
        'MEM': 'Memphis',
        'NYK': 'NewYork',
        'TOR': 'Toronto',
        'ATL': 'Atlanta',
        'HOU': 'Houston',
        'ORL': 'Orlando',
        'MIA': 'Miami',
        'NOP': 'NewOrleans',
        'GSW': 'GoldenState',
        'POR': 'Portland',
        'UTA': 'Utah',
        'MIN': 'Minnesota',
        'CHI': 'Chicago',
        'LAC': 'LAClippers',
        'OKC': 'OklahomaCity',
        'SAC': 'Sacramento',
        'PHX': 'Phoenix',
        'CHA': 'Charlotte',
        'WAS': 'Washington',
        'PHI': 'Philadelphia',
        'DET': 'Detroit',
        'CLE': 'Cleveland',
        'MIL': 'Milwaukee',
        'BKN': 'Brooklyn',
        'IND': 'Indiana',
        'LA Lakers': 'LALakers',
        'New York': 'NewYork',
        'LA Clippers': 'LAClippers',
        'Golden State': 'GoldenState',
        'New Orleans': 'NewOrleans',
        'Okla City': 'OklahomaCity',
        'San Antonio': 'SanAntonio'
}

## Path for the raw data
path = '/users/brodyvogel/Downloads/'


## Read and modify odds ###################################################
odds_2023 = pd.read_csv(path + 'NBA Odds 2023.csv')
odds_2023 = odds_2023.loc[odds_2023.KEEP == 1].reset_index(drop = True)
odds_2023['SEASON'] = 2023
odds_2022 = pd.read_csv(path + 'NBA Odds 2022.csv')
odds_2022 = odds_2022.loc[odds_2022.KEEP == 1].reset_index(drop = True)
odds_2022['SEASON'] = 2022
odds_2021 = pd.read_csv(path + 'NBA Odds 2021.csv')
odds_2021 = odds_2021.loc[odds_2021.KEEP == 1].reset_index(drop = True)
odds_2021['SEASON'] = 2021

odds = pd.concat([odds_2021, odds_2022, odds_2023]).reset_index(drop = True)
del (odds_2021, odds_2022, odds_2023)

odds['1H_END'] = odds[['H_1Q', 'H_2Q', 'V_1Q', 'V_2Q']].sum(axis = 1)
odds['1H_H_SPREAD_END'] = (odds['H_1Q'] + odds['H_2Q']) - (odds['V_1Q'] + odds['V_2Q'])
odds['FINAL_TOTAL'] = odds['H_FINAL'] + odds['V_FINAL']
odds['FINAL_SPREAD_H'] = odds['H_FINAL'] - odds['V_FINAL']
odds['H_SPREAD_CLOSE'] = -1 * odds['V_SPREAD_CLOSE']
odds['PERCENT_OF_TOTAL'] = odds['1H_END'] / odds['FINAL_TOTAL']

odds = odds[['Date', 'VISITOR', 'HOME', 'TOTAL_CLOSE', 'H_SPREAD_CLOSE', '1H_END', '1H_H_SPREAD_END', 'FINAL_TOTAL',
       'FINAL_SPREAD_H', '2H_TOTAL', 'PERCENT_OF_TOTAL', 'SEASON']]

odds['Date'] = [str(x)[0:4] + '-' + str(x)[4:6] + '-' + str(x)[6:8] for x in odds['Date']]
odds['YEAR_MONTH'] = [str(x)[0:7] for x in odds['Date']]

# Calculate the recent pace (over the last 10 games) for every team
recent_pace = pd.DataFrame({'team': [], 'Date': [], 'recent_pace': []})
for team in odds['VISITOR'].unique():
        all_games = odds.loc[(odds.VISITOR == team) | (odds.HOME == team)]
        for season in odds['SEASON'].unique():
                season_games = all_games.loc[all_games.SEASON == season]
                for day in season_games.Date.unique():
                        truncated_games = season_games.loc[season_games.Date < day].reset_index(drop = True)
                        recent_pace.loc[len(recent_pace)] = [team, day, truncated_games.loc[len(truncated_games)-10:, ].PERCENT_OF_TOTAL.mean()]
#############################################################################


## Read and modify TR data #############################################################################
data_2023 = pd.read_csv(path + '2022.csv')
data_2022 = pd.read_csv(path + '2021.csv')
data_2021 = pd.read_csv(path + '2020.csv')

data = pd.concat([data_2021, data_2022, data_2023]).reset_index(drop = True)
data = data[['team', 'opponent-true-shooting-percentage', 'personal-foul-pct', 'free-throw-rate', 'steal-pct',
                       'turnover-pct', 'possessions-per-game', 'true-shooting-percentage', 'Date']]

del([data_2021, data_2022, data_2023])

# fix the team names in the TR data
for x in range(len(data)):
        try:
                data.loc[x, 'team'] = team_map[data.loc[x, 'team']]
        except:
                continue
#############################################################################

## Read and modify games #############################################################################
games_2021 = pd.read_csv(path + '2020-21_pbp.csv')
games_2022 = pd.read_csv(path + '2021-22_pbp.csv')
games_2023 = pd.read_csv(path + '2022-23_pbp.csv')
games = pd.concat([games_2021, games_2022, games_2023]).reset_index(drop = True)

del(games_2021, games_2022, games_2023)

games = games[['actionNumber', 'timeActual', 'period', 'actionType', 'subType',
       'scoreHome', 'scoreAway', 'teamTricode', 'gameid']]

hist = pd.DataFrame({"game_id": [], "game_date": [], "ht_ts_perc": [], "ht_opp_personal_foul_pct": [], "ht_ftr": [],
                     "ht_to_perc": [], "ht_poss_pg": [], "ht_steals": [], "ht_poss": [], "ht_steal_perc": [], "ht": [],
                     "at_ts_perc": [], "at_opp_personal_foul_pct": [], "at_ftr": [], "at_to_perc": [], "at_poss_pg": [],
                     "at_steals": [], "at_poss": [], "at_steal_perc": [], "at": []})

# Processes each game to get the summarized data
for game in games.gameid.unique():
        game_id = game
        game_date = games.loc[games.gameid == game]['timeActual'].min()
        home, away = process_game(games, game)
        ht_ts_perc = home[0]
        ht_opp_personal_foul_pct = home[1]
        ht_ftr = home[2]
        ht_to_perc = home[3]
        ht_poss_pg = home[4]
        ht_steals = home[5]
        ht_poss = home[6]
        ht_steal_perc = home[7]
        ht = home[8]
        at_ts_perc = away[0]
        at_opp_personal_foul_pct = away[1]
        at_ftr = away[2]
        at_to_perc = away[3]
        at_poss_pg = away[4]
        at_steals = away[5]
        at_poss = away[6]
        at_steal_perc = away[7]
        at = away[8]

        new_row = [game_id, game_date, ht_ts_perc, ht_opp_personal_foul_pct, ht_ftr, ht_to_perc, ht_poss_pg, ht_steals, ht_poss, ht_steal_perc, ht,
                   at_ts_perc, at_opp_personal_foul_pct, at_ftr, at_to_perc, at_poss_pg, at_steals, at_poss, at_steal_perc, at]

        hist.loc[len(hist)] = new_row
        print('Finished: ', game_id)

hist['hours'] = [x[11:13] for x in hist['game_date']]
hist['game_date'] = [x[0:10] for x in hist['game_date']]
hist['alt_date'] = [(datetime.datetime.strptime(x, '%Y-%m-%d') - datetime.timedelta(days = 1)).strftime('%Y-%m-%d') for x in hist['game_date']]
hist['Date'] = [hist['game_date'][x] if int(hist['hours'][x]) - 6 > 0 else hist['alt_date'][x] for x in range(len(hist))]

# fix the team names in the pbp data
for x in range(len(hist)):
        hist.loc[x, 'ht'] = team_map[hist.loc[x, 'ht']]
        hist.loc[x, 'at'] = team_map[hist.loc[x, 'at']]
#############################################################################

## gross joins #############################################################################
big = hist.merge(odds, how = 'left', right_on = ['Date', 'VISITOR', 'HOME'], left_on = ['Date', 'at', 'ht'])
big = big.merge(data, how = 'left', left_on = ['Date', 'VISITOR'], right_on = ['Date', 'team'])
big = big.merge(data, how = 'left', left_on = ['Date', 'HOME'], right_on = ['Date', 'team'])
big = big.merge(recent_pace, how = 'left', left_on = ['Date', 'VISITOR'], right_on = ['Date', 'team'])
big = big.merge(recent_pace, how = 'left', left_on = ['Date', 'HOME'], right_on = ['Date', 'team'])

big.columns = ['game_id', 'game_date', 'ht_ts_perc', 'ht_opp_personal_foul_pct',
       'ht_ftr', 'ht_to_perc', 'ht_poss_pg', 'ht_steals', 'ht_poss',
       'ht_steal_perc', 'ht', 'at_ts_perc', 'at_opp_personal_foul_pct',
       'at_ftr', 'at_to_perc', 'at_poss_pg', 'at_steals', 'at_poss',
       'at_steal_perc', 'at', 'hours', 'alt_date', 'Date', 'VISITOR', 'HOME',
       'TOTAL_CLOSE', 'H_SPREAD_CLOSE', '1H_END', '1H_H_SPREAD_END',
       'FINAL_TOTAL', 'FINAL_SPREAD_H', '2H_TOTAL', 'PERCENT_OF_TOTAL', 'SEASON', 'YEAR_MONTH', 'team_at',
       'opponent-true-shooting-percentage_at', 'personal-foul-pct_at',
       'free-throw-rate_at', 'steal-pct_at', 'turnover-pct_at',
       'possessions-per-game_at', 'true-shooting-percentage_at', 'team_ht',
       'opponent-true-shooting-percentage_ht', 'personal-foul-pct_ht',
       'free-throw-rate_ht', 'steal-pct_ht', 'turnover-pct_ht',
       'possessions-per-game_ht', 'true-shooting-percentage_ht', 'crap', 'recent_pace_at', 'bag', 'recent_pace_ht']


## Create the fucking factors
big['PREGAME_TOTAL'] = big['TOTAL_CLOSE']
big['HALFTIME_TOTAL'] = big['1H_END']
big['PREGAME_HT_SPREAD'] = big['H_SPREAD_CLOSE']
big['HALFTIME_HT_SPREAD'] = big['1H_H_SPREAD_END']
big['TRUE_SHOOTING_OBSERVED'] = 200 * ((big['ht_ts_perc'] + big['at_ts_perc']) / 2)
big['FOUL_PERC_OBSERVED'] = 100 * ((big['ht_opp_personal_foul_pct'] + big['at_opp_personal_foul_pct']) / 2)
big['FREE_THROW_RATE_OBSERVED'] = 100 * ((big['ht_ftr'] + big['at_ftr']) / 2)
big['TURNOVER_PERC_OBSERVED'] = 100 * ((big['ht_to_perc'] + big['at_to_perc']) / 2)
big['PACE_OBSERVED'] = (big['ht_poss_pg'] + big['at_poss_pg']) / 2
big['TRUE_SHOOTING_EXPECTED'] = (((big['opponent-true-shooting-percentage_at'] + big['true-shooting-percentage_ht']) / 2) + ( (big['opponent-true-shooting-percentage_ht'] + big['true-shooting-percentage_at']) / 2 ) ) / 2
big['TRUE_SHOOTING_DIFFERENTIAL'] = big['TRUE_SHOOTING_OBSERVED'] - big['TRUE_SHOOTING_EXPECTED']
big['FOUL_PERC_EXPECTED'] = (big['personal-foul-pct_at'] + big['personal-foul-pct_ht']) / 2
big['FOUL_PERC_DIFFERENTIAL'] = big['FOUL_PERC_OBSERVED'] - big['FOUL_PERC_EXPECTED']
big['FREE_THROW_RATE_EXPECTED'] = (big['free-throw-rate_at'] + big['free-throw-rate_ht']) / 2
big['FREE_THROW_RATE_DIFFERENTIAL'] = big['FREE_THROW_RATE_OBSERVED'] - big['FREE_THROW_RATE_EXPECTED']
big['TURNOVER_PERC_EXPECTED'] = (big['turnover-pct_at'] + big['turnover-pct_ht']) / 2
big['TURNOVER_PERC_DIFFERENTIAL'] = big['TURNOVER_PERC_OBSERVED'] - big['TURNOVER_PERC_EXPECTED']
big['PACE_EXPECTED'] = (big['possessions-per-game_at'] + big['possessions-per-game_ht']) / 2
big['PACE_DIFFERENTIAL'] = big['PACE_OBSERVED'] - big['PACE_EXPECTED']
big['RECENT_PACE'] = (big['recent_pace_at'] + big['recent_pace_ht']) / 2

big['YEAR_MONTH'] = [x[0:7] for x in big['Date']]

data_big = big[['PREGAME_TOTAL', 'HALFTIME_TOTAL', 'PREGAME_HT_SPREAD',
       'HALFTIME_HT_SPREAD', 'TRUE_SHOOTING_OBSERVED', 'TRUE_SHOOTING_EXPECTED',
        'FOUL_PERC_OBSERVED','FOUL_PERC_EXPECTED',
       'FREE_THROW_RATE_OBSERVED','FREE_THROW_RATE_EXPECTED', 'TURNOVER_PERC_OBSERVED', 'TURNOVER_PERC_EXPECTED',
        'PACE_OBSERVED', 'PACE_EXPECTED', 'TRUE_SHOOTING_DIFFERENTIAL', 'FOUL_PERC_DIFFERENTIAL',
        'FREE_THROW_RATE_DIFFERENTIAL', 'TURNOVER_PERC_DIFFERENTIAL', 'PACE_DIFFERENTIAL',
        'Date', 'YEAR_MONTH', 'VISITOR', 'HOME',
        'FINAL_TOTAL', '2H_TOTAL', 'RECENT_PACE']]

data_big['OUTCOME'] = [
    'OVER' if ((data_big['FINAL_TOTAL'][x] - data_big['HALFTIME_TOTAL'][x]) - data_big['2H_TOTAL'].astype(float)[x]) >= 10
    else 'UNDER' if ((data_big['FINAL_TOTAL'][x] - data_big['HALFTIME_TOTAL'][x]) - data_big['2H_TOTAL'].astype(float)[x]) <= -10
    else 'INLINE'for x in range(len(data_big))
]

data_big['OUTCOME_UNDER'] = [
    '1' if ((data_big['FINAL_TOTAL'][x] - data_big['HALFTIME_TOTAL'][x]) - data_big['2H_TOTAL'].astype(float)[x]) <= -10
    else '0'for x in range(len(data_big))
]

data_big['OUTCOME_OVER'] = [
    '1' if ((data_big['FINAL_TOTAL'][x] - data_big['HALFTIME_TOTAL'][x]) - data_big['2H_TOTAL'].astype(float)[x]) >= 10
    else '0'for x in range(len(data_big))
]

data_big['ACTUALS'] = data_big['FINAL_TOTAL'] - data_big['HALFTIME_TOTAL']
data_big['ACTUAL_PLAY'] = ['OVER' if float(data_big['ACTUALS'][x]) > float(data_big['2H_TOTAL'][x]) else 'UNDER' for x in range(len(data_big))]

data_big['HT_EXPECTATION'] = data_big['PREGAME_TOTAL'] / 2 + 1

data_big.to_csv(path + 'data_big.csv', index = False)
#############################################################################