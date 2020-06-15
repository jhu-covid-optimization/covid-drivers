import numpy as np
import pandas as pd
from pathlib import Path
import re
from ..utils.dates import str2date, switch_date_format, ordinal2string, lag_date
from ..utils.df_utils import get_date_columns
from ..pandas.align import align_lagged_dates

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

def load_infection_time_series(standardize_dates=True):
    csv_path, date = _get_file(raw_dir, 'infection_time_series')
    infections_ts = pd.read_csv(raw_dir / csv_path, parse_dates = True)

    if standardize_dates:
        infections_ts.rename(columns={c:switch_date_format(c,"%m/%d/%y") for c in infections_ts.columns}, inplace=True)

    return(infections_ts,date)

def load_descartes_m50(standardize_dates=True):
    csv_path, date = _get_file(raw_dir, 'descartes_m_50')
    df = pd.read_csv(raw_dir / csv_path, parse_dates = True)

    if standardize_dates:
        df.rename(columns={c:switch_date_format(c,"%Y-%m-%d") for c in df.columns}, inplace=True)
    
    df.rename(columns={'fips':'FIPS'}, inplace=True)
    df.dropna(axis=0, subset=['admin2'], inplace=True)
    df['FIPS'] = df['FIPS'].astype(int)

    return(df,date)

def load_od_baseline():
    od_mobility = pd.read_csv('../data/processed/od_mobility_baseline.csv')
    return od_mobility

def load_acute_care(beds=True):
    hospitals = pd.read_csv('../data/processed/Hospitals.csv')
    hospitals = hospitals[['TYPE', 'STATUS', 'COUNTYFIPS', 'BEDS']]
    hospitals = hospitals[hospitals["STATUS"] == 'OPEN']
    hospitals = hospitals[hospitals["TYPE"] == 'GENERAL ACUTE CARE']
    if beds:
        hospitals = hospitals[hospitals["BEDS"].astype(str).astype(int) > 0]
    hospitals["FIPS"] = hospitals["COUNTYFIPS"]
    hospitals = hospitals[hospitals["FIPS"] != 'NOT AVAILABLE']
    hospitals = hospitals.drop(["COUNTYFIPS", "STATUS"], axis=1)
    hospitals["FIPS"] = hospitals["FIPS"].astype(str).astype(int)
    hospitals = hospitals.groupby("FIPS")['BEDS'].agg(
        ['sum', 'count']).rename(columns={'sum':'Beds', 'count':'HospCt'}
        )
    hospitals.reset_index(inplace=True)

    return hospitals

def load_matthias_clusters():
    csv_path, date = _get_file(raw_dir, 'descartes_m_50')
    df = pd.read_csv('../data/processed/clustering.csv')
    df = df[['FIPS', 'cluster']]
    return df

def load_od_mobilities():
    csv_path, date = _get_file(processed_dir, 'od_inter_mobilities')
    mobility_ts = pd.read_csv(processed_dir / csv_path, parse_dates = True)

    return mobility_ts, date

def get_cum_deaths_dataframe(n_days, onset_threshold=3, time_series=False):
    """
    Returns a dataframe of static variables, mobility statistics, and deaths
    (cumulative) ndays out.
    

    Parameters
    ----------
    n_days : int
        Number of days out to record deaths
    onset_threshold : int
        Death threshold to mark a county outbreak start.
    time_series : boolean (default=False)
    """

    # Time series data
    mobility, mobility_date = load_google_mobility()
    deaths, deaths_date = load_deaths(join_county_codes=False)
    interventions, interventions_date = load_interventions()
    # Static data
    counties, counties_date = load_counties()
    # Processed mobility -> time series
    mobility_ts, mobility_ts_date = load_google_mobility_time_series()
    m50,_ = load_descartes_m50()
    od_mobilities, _ = load_od_mobilities()
    hospitals = load_acute_care(beds=True)
    ## Get death dataframe date columns
    death_dates = get_date_columns(deaths, return_dtimes=False)
    ## Moving average (weekly) mobility
    od_mobilities_ma = od_mobilities.copy()
    od_mobilities_ma[od_mobilities_ma.columns[1:]] = od_mobilities[
        od_mobilities.columns[1:]
        ].rolling(7, center=True, axis=1).mean()
    od_mobilities_ma = od_mobilities_ma.dropna(axis=1)
    deaths_df = deaths[['FIPS']+death_dates]
    deaths_df.dropna(subset=['FIPS'], inplace=True)
    deaths_df = deaths_df.astype({'FIPS':int})
    deaths_df['onset'] = deaths_df[death_dates].apply(
        lambda row: _get_onset_date(row, thresh=onset_threshold), axis=1)
    ## Drop counties with no onset
    deaths_df = deaths_df.dropna(axis=0, subset=['onset'])
    ## Only counties with N_DAYS worth of data after onset
    deaths_df = deaths_df[deaths_df['onset'].apply(
        lambda d: (str2date(death_dates[-1]) - str2date(d)).days >= n_days
    )]
    ## Remove counties with growth decrease, in case of errors
    deaths_df = deaths_df[
        deaths_df.apply(
            lambda r: r[[d for d in death_dates if 
                str2date(d) >= str2date(r['onset']) and 
                str2date(d) <= lag_date(str2date(r['onset']
            ), 
            lag=n_days, backwards=False)
                        ]].diff().min() >= 0, axis=1
        )
    ]
    ## Get the number of deaths or timeseries to N_DAYS from onset
    ## and make final dataframe
    if time_series:
        for days_past in range(n_days):
            deaths_df[f'day_{days_past+1:02d}'] = deaths_df.apply(
                lambda row: row[lag_date(row['onset'], days_past, backwards=False, return_date=False)],axis=1
            )
        cum_deaths = deaths_df[['FIPS'] + [f'day_{d+1:02d}' for d in range(n_days)] + ['onset']]
    else:
        deaths_df['cum_deaths'] = deaths_df.apply(
            lambda r: r[lag_date(str2date(r['onset']), lag=n_days, backwards=False, return_date=False)], axis=1
        )
        
        cum_deaths = deaths_df[['FIPS', 'cum_deaths', 'onset']]
    cum_deaths = pd.merge(cum_deaths, hospitals, on='FIPS')
    ## OD baseline
    od_dates = get_date_columns(od_mobilities, return_dtimes=False)
    od_mobilities['OD_baseline'] = od_mobilities.apply(lambda x: x[od_dates[:14]].mean(), axis=1)
    cum_deaths = pd.merge(cum_deaths, od_mobilities[['FIPS', 'OD_baseline']], on='FIPS')
    ## OD at onset
    new_row = []
    for i,row in cum_deaths.iterrows():
        try:
            od = od_mobilities_ma[od_mobilities_ma['FIPS']==row['FIPS']][row['onset']].iloc[0]
        except:
            od = np.nan
        new_row.append(od)
    cum_deaths['OD_at_onset'] = new_row
    ## OD 2 weeks before onset
    new_row = []
    for i,row in cum_deaths.iterrows():
        try:
            lag_onset = lag_date(row['onset'], lag=14, backwards=True, return_date=False)
            od = od_mobilities_ma[od_mobilities_ma['FIPS']==row['FIPS']][lag_onset].iloc[0]
        except:
            od = np.nan
        new_row.append(od)
    cum_deaths['OD_2wk_before_onset'] = new_row
    ## OD 2 weeks after onset
    new_row = []
    for i,row in cum_deaths.iterrows():
        try:
            lag_onset = lag_date(row['onset'], lag=14, backwards=False, return_date=False)
            od = od_mobilities_ma[od_mobilities_ma['FIPS']==row['FIPS']][lag_onset].iloc[0]
        except:
            od = np.nan
        new_row.append(od)
    cum_deaths['OD_2wk_after_onset'] = new_row
    ## static features
    static_features = counties[
        ['FIPS',
        'Rural-urban_Continuum Code_2013',
        'Density per square mile of land area - Population',
        'Percent of adults with less than a high school diploma 2014-18',
        'PCTPOV017_2018',
        'Unemployment_rate_2018',
        'Total_age65plus', 
        'POP_ESTIMATE_2018']
    ]
    static_features = static_features.dropna()
    cum_deaths = cum_deaths.merge(static_features, on="FIPS")
    ## Outliers
    outliers = [36061, 6038, 17031, 48201]
    cum_deaths = cum_deaths[~cum_deaths['FIPS'].isin(outliers)]

    return cum_deaths


#################################
# Utility Functions
#################################
def _get_onset_date(row, thresh):
    above = row[row >= thresh]
    if len(above) == 0:
        return np.nan
    else:
        return above.idxmin()