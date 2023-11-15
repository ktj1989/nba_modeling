import requests
import pandas as pd
import numpy as np
import io
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
import matplotlib.pyplot as plt
from typing import List
import nba_modeling.data.utilities as utl


SEASON = '2023-24'
PATH = './stored_data'

class NBASeasonFetcher:
    def __init__(self, season):
        self.season = season
        self.game_metadata = self.fetch_season_metadata()
        self.finished_game_ids = self.calc_finished_game_ids(game_metadata=self.game_metadata)
        self.game_pbp = self.fetch_pbp(game_ids=self.finished_game_ids)

    def fetch_season_metadata(self) -> pd.DataFrame:

        gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable=SEASON,
                                                       league_id_nullable='00',
                                                       season_type_nullable='Regular Season')
        games = gamefinder.get_data_frames()[0]

        return games

    def calc_finished_game_ids(self, game_metadata) -> List[str]:
        return game_metadata[~game_metadata['WL'].isna()]['GAME_ID'].unique().tolist()

    def fetch_pbp(self, game_ids: List[str]) -> pd.DataFrame:
        pbpdata = []
        total_loop = 1
        for game_id in game_ids:
            print(f'Season: {self.season} Game id: {game_id} is {total_loop} of {len(game_ids)}')
            game_data = utl.get_data(game_id)
            pbpdata.append(game_data)
            total_loop += 1 # increment

        df = pd.concat(pbpdata, ignore_index=True)
        return df

    def write_data(self):
        game_pbp_path = f'{PATH}/{SEASON}_pbp.csv'
        print(f'Writing game pbp to .{game_pbp_path}')
        self.game_pbp.to_csv(game_pbp_path, index=False)
        game_metadata_path = f'{PATH}/{SEASON}_metadata.csv'
        print(f'Writing game metadata to {game_metadata_path}')
        self.game_metadata[self.game_metadata['GAME_ID'].isin(self.finished_game_ids)].to_csv(game_metadata_path, index=False)


for season in ['2023-24', '2022-23', '2021-22']:
    nba_season = NBASeasonFetcher(season=season)
    nba_season.write_data()
