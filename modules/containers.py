import os
import json
from datetime import datetime


class PushShiftPost(object):
    """
    Reddit post retrieved from PushShift API
    """
    def __init__(self, data):
        """
        data: JSON returned by PushShift API, containing a single post.
        """
        if type(data) is not dict:
            data = json.load(data)

        self.data = data


    @classmethod
    def from_json(cls, data):
        return cls(data)

    @property
    def subreddit(self):
        return self.data["subreddit"]
    
    @property
    def id(self):
        return self.data["id"]

    @property
    def title(self):
        return self.data["title"]
    
    @property
    def permalink(self):
        return self.data["permalink"]
    
    @property
    def url(self):
        return self.data["url"]

    @property
    def created_utc(self, datetime=False):
        return self._handle_timestamp(self.data["created_utc"]) if datetime == True else self.data["created_utc"]


    def _handle_timestamp(self, value):
        if type(value) is isinstance(value, datetime):
            return value
        elif type(value) is float or type(value) is int:
            return datetime.fromtimestamp(value)
        else:
            raise ValueError(f"Invalid time format/value encountered: {value}.")


class RedditPost(object):
    """
    Reddit post container with properties from the json.
    """
    def __init__(self, data):
        """
        data: JSON returned by Reddit API, containing a single post.
        """
        if type(data) is not dict:
            data = json.load(data)

        self.data = data


    @classmethod
    def from_json(cls, data):
        return cls(data)


    @classmethod
    def from_file(cls, path):
        with open(path, "r") as f:
            data = json.load(f)

        return cls.from_json(data)


    def __getattr__(self, property_name):
        if property_name not in self.data:
            return None

        return self.data[property_name]
    
    @property
    def removed(self):
        return self.data["selftext"] == "[removed]"

    @property
    def created_datetime(self):
        return self._handle_timestamp(self.data["created"])
    
    @property
    def created_utc_datetime(self):
        return self._handle_timestamp(self.data["created_utc"])

    def _handle_timestamp(self, value):
        # not used for now
        if type(value) is isinstance(value, datetime):
            return value
        elif type(value) is float or type(value) is int:
            return datetime.fromtimestamp(value)
        else:
            raise ValueError(f"Invalid time format/value encountered: {value}.")
