from pytz import timezone, utc
from datetime import datetime, timedelta


def localize(d, zone=None):
    if isinstance(zone, str) and zone:
        tz = timezone(zone)
    elif zone:
        tz = zone
    else:
        tz = timezone('Europe/Moscow')

    return tz.localize(d)


def toUTC(d):
    return d.astimezone(utc)


def timezone_now(zone=None):
    if isinstance(zone, str) and zone:
        tz = timezone(zone)
    elif zone:
        tz = zone
    else:
        tz = timezone('Europe/Moscow')

    return datetime.now(tz)


def gts():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S - ")


def extract_date(S):
    try:
        return datetime.strptime(S, '%Y-%m-%d')
    except:
        return None
