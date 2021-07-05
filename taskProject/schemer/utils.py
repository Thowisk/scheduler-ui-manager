from datetime import datetime

def date_and_time_to_datetime(date, time):
    """
    :param date: hh:mm:ss
    :param time: yyyy-mm-dd
    :return: datetime.datetime(yyyy, mm, dd, hh, min, ss)
    """
    yyyy, mm, dd = date.__str__().split('-')
    hh, min, ss = time.__str__().split(':')

    date = datetime(int(yyyy), int(mm), int(dd), int(hh), int(min), int(ss))
    return date

