import pandas as pd
from .dates import str2date,date2str
from datetime import datetime

def get_date_columns(df, return_dtimes=True):
    cols = df.columns
    dates = []
    for c in cols:
        try:
            dates.append(str2date(c))
        except:
            continue
    if return_dtimes:
        return(dates)
    else:
        return([date2str(d) for d in dates])