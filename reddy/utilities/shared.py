from datetime import datetime, timedelta


def time_to_unix(value):
    """
    Returns unix time or time difference in seconds.
    """
    if isinstance(value, datetime):
        return value.timestamp()
    elif isinstance(value, timedelta):
        return value.total_seconds()
    elif type(value) is float or type(value) is int:
        return value
    else:
        raise ValueError(f"Invalid time format/value encountered: {value}.")


def time_to_hms(time):
    """
    """
    m, s = divmod(time_to_unix(time), 60)
    h, m = divmod(m, 60)
    return h, m, s
