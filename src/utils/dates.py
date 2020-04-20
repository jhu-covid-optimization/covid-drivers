from datetime import datetime

dtime_format = "%m-%d"

def date2str(date):
    return

def str2date(string):
    return(datetime.strptime(string, dtime_format))

def get_today(string=True):
    today = datetime.now().strftime(dtime_format)
    if string:
        return today
    else:
        return(str2date(today))
