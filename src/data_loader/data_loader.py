import numpy as np
import pandas as pd
from pathlib import Path
import re
from src.utils.dates import str2date
import os

data_dir = Path('../data')
raw_dir = data_dir / 'raw'

def _get_file(path, name):
    files = []
    dtimes = []
    query = f'{name}_(.+?).csv'
    for f in os.listdir(path):
        match = re.search(query, f)
        if match:
            files.append(f)
            dtimes.append(match.group(1))

    return(max(zip(files,dtimes), key=lambda x: str2date(x[1])))

def load_google_mobility():
    csv_path, date = _get_file(raw_dir, 'time_series_covid19_deaths_US')
    csv = pd.read_csv(raw_dir / csv_path, parse_dates = True)

    return(csv, date)