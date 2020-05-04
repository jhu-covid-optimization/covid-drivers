import numpy as np
import pandas as pd
from pathlib import Path
import re
from ..utils.dates import str2date, switch_date_format, ordinal2string
import os

data_dir = Path('../data')
raw_dir = data_dir / 'raw'
processed_dir = data_dir / 'processed'

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

def load_deaths(join_county_codes = False, drop_geo=False, standardize_dates=True):
    deaths_path, date = _get_file(raw_dir, 'time_series_covid19_deaths_US')
    deaths = pd.read_csv(raw_dir / deaths_path, parse_dates = True)
    if drop_geo or join_county_codes:
        deaths = deaths.drop(labels=['UID', 'iso2', 'iso3', 'code3', 'Admin2', 'Province_State', 'Country_Region', 'Lat', 'Long_', "Combined_Key", "Population"], axis=1)
    if join_county_codes:
        county_codes = load_counties()[0][['FIPS', 'Rural-urban_Continuum Code_2013']]
        deaths = pd.merge(deaths, county_codes, on="FIPS")
    if standardize_dates:
        deaths.rename(columns={c:switch_date_format(c,"%m/%d/%y") for c in deaths.columns}, inplace=True)

    return(deaths, date)

def load_interventions(standardize_dates = True):
    csv_path, date = _get_file(raw_dir, 'interventions')
    interventions = pd.read_csv(raw_dir / csv_path, parse_dates = True)

    if standardize_dates:
        interventions.iloc[:,3:] = interventions.iloc[:,3:].applymap(ordinal2string)

    return(interventions, date)

def load_google_mobility(remove_foreign=True):
    csv_path, date = _get_file(raw_dir, 'google_mobility_report')
    mobility = pd.read_csv(raw_dir / csv_path, parse_dates = True)
    
    if remove_foreign:
        mobility = mobility[mobility.loc[:,'country_region_code'] == 'US']
        mobility.drop(labels=['country_region_code', 'country_region'], axis=1, inplace=True)
        mobility.dropna(axis='rows',subset=['sub_region_1','sub_region_2'], inplace=True)
        mobility.rename(columns={'sub_region_1':'state','sub_region_2':'county'}, inplace=True)

    return(mobility, date)

def load_counties():
    csv_path, date = _get_file(raw_dir, 'counties')
    csv = pd.read_csv(raw_dir / csv_path, parse_dates = True)

    return(csv, date)

def load_google_mobility_time_series():
    csv_path, date = _get_file(processed_dir, 'mobility_time_series')
    mobility_ts = pd.read_csv(processed_dir / csv_path, parse_dates = True)

    return(mobility_ts,date)