import json
import requests
import warnings
from datetime import datetime, timedelta, timezone

from .containers import PushShiftPost


class PushshiftAPI(object):
    """
    Simple wrapper for some Pushshift API.
    See https://pushshift.io/api-parameters/ or https://github.com/pushshift/api
    """

    def __init__(self):
        self._header = {"User-Agent": "python:reddy:v0.1 (by /u/timberhilly)"}

    def _normalize_time_parameter(self, t, tolerance=10):
        if t is None:
            return ""

        def isnumber(t): return isinstance(t, int) or isinstance(t, float)
        def tounixtime(dt_obj): return dt_obj.replace(
            tzinfo=timezone.utc).timestamp()

        if isnumber(t):
            # this is unix time
            t = (t-tolerance, t+tolerance)
        elif isinstance(t, datetime):
            # this is a datetime object
            unix_time = tounixtime(t)
            t = (unix_time-tolerance, unix_time+tolerance)
        elif isinstance(t, tuple) and isinstance(t[0], datetime) and isinstance(t[1], datetime):
            # this is a datetime range
            t = (tounixtime(t[0]), tounixtime(t[1]))
        elif isinstance(t, tuple) and isnumber(t[0]) and isnumber(t[1]):
            pass
        else:
            raise ValueError(
                "Wrong value encountered in cache.select(t=???). Use datetime object or unix time, or a tuple.")

        return f"{t[0]}..{t[1]}"

    def search(self, subreddit, query=None, t=None, before=None, after=None, limit=500):
        """
        Search subreddit API client.

        subreddit, str: name of the subreddit.

        subreddit, str: search terms.

        t, int/float/datetime/tuple: time or list of times as unix time or python datetime object in UTC (optional)
        """
        created_utc = self._normalize_time_parameter(t)
        base_url = "https://api.pushshift.io/reddit/search/submission/"

        if limit > 500:
            limit = 500
        elif limit < 0:
            limit = 0

        response = requests.get(base_url, dict(
            subreddit=subreddit,
            q=query,
            before=before,
            after=after,
            size=limit,
        ), headers=self._header)

        response.raise_for_status()
        response_dictionary = json.loads(response.content)

        return [PushShiftPost(data) for data in response_dictionary["data"]]
