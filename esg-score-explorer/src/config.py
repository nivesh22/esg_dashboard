from pathlib import Path

class Config:
    def __init__(self):
        self.data_dir = Path(__file__).resolve().parent / 'data'
        self.raw_data_dir = self.data_dir / 'raw'
        self.processed_data_dir = self.data_dir / 'processed'
        self.esg_scores_file = self.processed_data_dir / 'esg_demo_enriched.csv'
        self.default_year = 2023
        self.default_rows = 1000

    def get_esg_scores_path(self):
        return self.esg_scores_file

    def get_raw_data_path(self):
        return self.raw_data_dir

    def get_processed_data_path(self):
        return self.processed_data_dir

config = Config()