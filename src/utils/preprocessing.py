import numpy as np
import pandas as pd

def moving_average(df, cols, n=3):
    df = df.copy()
    df[cols] = df[cols].apply(lambda x: x.rolling(window=n).mean(), axis=1)
    df.drop(cols[:n-1] , axis=1, inplace=True)

    return df