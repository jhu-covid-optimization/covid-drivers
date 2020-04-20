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

def load_deaths(join_county_codes = False, drop_geo=False):
    deaths_path, date = _get_file(raw_dir, 'time_series_covid19_deaths_US')
    death = pd.read_csv(raw_dir / deaths_path, parse_dates = True)

    if drop_geo or join_county_codes:
        deaths = deaths.drop(labels=['UID', 'iso2', 'iso3', 'code3', 'Admin2', 'Province_State', 'Country_Region', 'Lat', 'Long_', "Combined_Key", "Population"], axis=1)
    if join_county_codes:
        county_codes = load_counties()[0][['FIPS', 'Rural-urban_Continuum Code_2013']]
        deaths = deaths.merge(county_codes, on="FIPS")

    return(deaths, date)

def load_interventions():
    csv_path, date = _get_file(raw_dir, 'interventions')
    csv = pd.read_csv(raw_dir / csv_path, parse_dates = True)

    return(csv, date)

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

def load_google_mobility_time_series(
    subset=['retail_and_recreation']
):
    """
    subset : array-like
        subset of regions to average together. Elements are of
        ['retail_and_recreation','grocery_and_pharmacy', 'parks',
        'transit_stations','workplaces','residential']
    """
    all_regions = ['retail_and_recreation','grocery_and_pharmacy', 'parks',
        'transit_stations','workplaces','residential']
    all_regions = [s + '_percent_change_from_baseline' for s in all_regions]
    subset = [s + '_percent_change_from_baseline' for s in subset]
    mobility,date = load_google_mobility()
    # Drop rows with na in column(s) of interest
    mobility.dropna(axis='rows', subset=subset, inplace=True)
    # Average column(s) of interest and make a new column
    mobility['mean_percent_change'] = mobility[subset].mean(axis='columns')
    # Remove all old data columns
    mobility.drop(axis='columns',labels=all_regions, inplace=True)
    # Pivot to form time series
    mobility = mobility.pivot_table(
                    index=['state', 'county'],
                    columns='date',
                    values='mean_percent_change',
                    aggfunc='first'
                ).reset_index()

    return(mobility,date)