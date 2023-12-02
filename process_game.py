import pandas as pd
import numpy as np

def process_team(df, home = True):
    # Get total points for the team
    if home == True:
        pts = df.scoreHome.max()
    else:
        pts = df.scoreAway.max()

    # get action types needed to compute statistic
    shots = df.loc[df.actionType.isin(['3pt', '2pt'])]['actionNumber'].count()
    fts = df.loc[df.actionType == 'freethrow']['actionNumber'].count()
    opp_fouls = df.loc[df.actionType == 'foul']['actionNumber'].count()
    poss = df.loc[df.actionType.isin(['3pt', '2pt', 'turnover'])]['actionNumber'].count()
    steals = df.loc[df.actionType == 'steal']['actionNumber'].count()
    tos = df.loc[df.actionType == 'turnover']['actionNumber'].count()

    # True Shooting %
    ts_perc = (0.5 * pts) / (shots + 0.475 * fts)

    # Opponent Personal Foul %
    opp_personal_foul_pct = opp_fouls / poss

    # Free Throw Rate
    ftr = fts / shots

    # Turnover %
    to_perc = tos / poss

    # Extrapolated Possessions per Game
    poss_pg = poss * 2

    # return everything of interest
    return ts_perc, opp_personal_foul_pct, ftr, to_perc, poss_pg, steals, poss

def process_game(data, id):
    # filter to game of interest only
    game = data.loc[data.gameid == id]

    # find end of the first half
    end_id = game.loc[(game.period == 2) & (game.actionType == 'period') & (game.subType == 'end')].index[0]
    game = game.iloc[:(end_id+1), :]

    # find home and away teams
    for x in range(1, 100):
        if game.loc[x, 'scoreHome'] > game.loc[x-1, 'scoreHome']:
            home_team = game.loc[x, 'teamTricode']
            away_team = list(game.teamTricode.unique()[~pd.isna(game.teamTricode.unique())])
            away_team.remove(home_team)
            away_team = away_team[0]
        break

    # home and away team events
    ht_events = game.loc[game.teamTricode == home_team].reset_index(drop = True)
    at_events = game.loc[game.teamTricode == away_team].reset_index(drop = True)

    # call function to get needed team data from 1H
    ht_ts_perc, ht_opp_personal_foul_pct, ht_ftr, ht_to_perc, ht_poss_pg, ht_steals, ht_poss = process_team(ht_events, True)
    at_ts_perc, at_opp_personal_foul_pct, at_ftr, at_to_perc, at_poss_pg, at_steals, at_poss = process_team(at_events, False)

    # calculate steal %, which requires data from both teams
    ht_steal_perc = ht_steals / at_poss
    at_steal_perc = at_steals / ht_poss

    #### import season data and model ####
    ######################################

    return('Work in Progress')