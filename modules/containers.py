import os
import json
from datetime import datetime


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

        return cls.from_json(data)\

    
    @property
    def subreddit(self):
        return self.data["subreddit"]
    
    @property
    def title(self):
        return self.data["title"]
    
    @property
    def downs(self):
        return self.data["downs"]
    
    @property
    def ups(self):
        return self.data["ups"]
    
    @property
    def total_awards_received(self):
        return self.data["total_awards_received"]
    
    @property
    def author_premium(self):
        return self.data["author_premium"]
    
    @property
    def created(self):
        return self.data["created"]
    
    @property
    def view_count(self):
        return self.data["view_count"]
    
    @property
    def id(self):
        return self.data["id"]
    
    @property
    def permalink(self):
        return self.data["permalink"]
    
    @property
    def url(self):
        return self.data["url"]
    
    @property
    def created(self, datetime=True):
        return self._handle_timestamp(self.data["created"]) if datetime == True else self.data["created"]
    
    @property
    def created_utc(self, datetime=True):
        return self._handle_timestamp(self.data["created_utc"]) if datetime == True else self.data["created_utc"]


    def _handle_timestamp(self, value):
        if type(value) is isinstance(value, datetime):
            return value
        elif type(value) is float or type(value) is int:
            return datetime.fromtimestamp(value)
        else:
            raise ValueError(f"Invalid time format/value encountered: {value}.")
