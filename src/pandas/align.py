import numpy as np
import pandas as pd
from datetime import datetime
import sys

sys.path.append("../")
from src.utils.dates import get_today, lag_date, date2str
from src.utils.df_utils import get_date_columns


def align_lagged_dates(df1, df2, match_col, lag=0, date_converter=date2str, return_idx = True):
    """
    Concatenates two dataframes by matching on the given column and
    lagging time series dates. Note that df1 preceeds df2, for instance
    in a causal viewpoint.

    df1,df2 : dataframes to concatenate
    match_col : the column to match rows across dataframes
    lag : the day lag for which df1 will preceed df2
    date_converter : method to read a header date
    """
    FIPS = list(set(df1[match_col]) & set(df2[match_col]))
    causes = df1[df1[match_col].isin(FIPS)]
    effects = df2[df2[match_col].isin(FIPS)]

    # Sort so that FIPS align
    causes = causes.sort_values(by=causes.columns.tolist()).reset_index(drop=True)
    effects = effects.sort_values(by=effects.columns.tolist()).reset_index(drop=True)

    # Get columns that are dates
    cause_dates = get_date_columns(df1)
    effect_dates = get_date_columns(df2)

    start_date = max(
        min(cause_dates), lag_date(min(effect_dates), lag=lag, backwards=True)
    )
    end_date = min(
        lag_date(max(cause_dates), lag=lag, backwards=False), max(effect_dates)
    )

    # Get cause and effect dates in string form
    cause_start = start_date
    cause_end = lag_date(end_date, lag=lag)
    effect_start = lag_date(start_date, lag=lag, backwards=False)
    effect_end = end_date

    cause_dates = [
        date_converter(c)
        for c in cause_dates
        if (c > cause_start and c < cause_end)
    ]
    effect_dates = [
        date_converter(c)
        for c in effect_dates
        if (c > effect_start and c < effect_end)
    ]

    # Adjusted time series, to align with given lag
    cause_ts = causes[cause_dates].to_numpy()
    effect_ts = effects[effect_dates].to_numpy()

    if return_idx == True:
        return (pd.concat(
            (
                causes[cause_dates + [match_col]].rename(
                    {cd: i for i, cd in enumerate(cause_dates)}, axis=1
                ),
                effects[effect_dates + [match_col]].rename(
                    {ed: i for i, ed in enumerate(effect_dates)}, axis=1
                ),
            ),
            axis=0,
        ),
        (cause_dates, effect_dates),
        list(range(len(cause_dates))))
    else:
        return (pd.concat(
            (
                causes[cause_dates + [match_col]].rename(
                    {cd: i for i, cd in enumerate(cause_dates)}, axis=1
                ),
                effects[effect_dates + [match_col]].rename(
                    {ed: i for i, ed in enumerate(effect_dates)}, axis=1
                ),
            ),
            axis=0,
        ),
        (cause_dates, effect_dates)
        )

