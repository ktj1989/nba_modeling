import pandas as pd
import numpy as np
from typing import Tuple

class PBPEnrichment:
    def __init__(self, season):
        self.season = season
        self.metadata, self.pbp = self._load_raw_data()


    def _load_raw_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        metadata = pd.read_csv(f'/stored_data/{self.season}_metadata.csv')
        pbp = pd.read_csv(f'/stored_data/{self.season}_pbp.csv')
        return metadata, pbp

    def write_enriched_data(self):
        pass

    def calculate_stats(self):
        pass

    def _calculate_breaks(self):
        pass