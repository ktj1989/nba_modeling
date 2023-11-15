import requests
import pandas as pd
import numpy as np
import io
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
import matplotlib.pyplot as plt
import nba_modeling.data.utilities as utl


SEASON = '2023-24'
PATH = './stored_data'



gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable=SEASON,
                                              league_id_nullable='00',
                                              season_type_nullable='Regular Season')
games = gamefinder.get_data_frames()[0]
# Get a list of distinct game ids
game_ids = games['GAME_ID'].unique().tolist()

finished_games = games[~games['WL'].isna()]['GAME_ID'].unique().tolist()



x=1
pbpdata = []
total_loop = 1
for game_id in finished_games[:4]:
    print(f'Game id: {game_id} is {total_loop} of {len(game_ids)}')
    game_data = utl.get_data(game_id)
    pbpdata.append(game_data)
    x=1

df = pd.concat(pbpdata, ignore_index=True)

df.to_csv(f'{PATH}/{SEASON}_pbp.csv', index=False)
games[games['GAME_ID'].isin(finished_games)].to_csv(f'{PATH}/{SEASON}_metadata.csv', index=False)