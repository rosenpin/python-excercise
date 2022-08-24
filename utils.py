import datetime


def formatted_time_to_unix_time(formatted_time, format):
    dt = datetime.datetime.strptime(formatted_time, format)
    return int(dt.timestamp())


def format_ymd_time_to_unix(formatted_time):
    return formatted_time_to_unix_time(formatted_time, '%Y-%m-%d')


# tests
assert format_ymd_time_to_unix("2018-12-15") == 1544824800
