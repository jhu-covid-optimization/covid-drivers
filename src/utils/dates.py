from datetime import datetime

dtime_format = "%m-%d"

def str2date(string, fmt=dtime_format):
    return(datetime.strptime(string, fmt))

def get_today(string=True):
    today = datetime.now().strftime(dtime_format)
    if string:
        return today
    else:
        return(str2date(today))

def switch_date_format(string, fmt1, fmt2=dtime_format):
    try:
        return(str2date(string, fmt1).strftime(fmt2))
    except:
        return(string)

def ordinal2string(ord, fmt=dtime_format):
    try:
        return(datetime.fromordinal(int(ord)).strftime(fmt))
    except:
        return(ord)
