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


    @property
    def id(self):
        return self.data["id"]
    
    @property
    def author(self):
        return self.data["author"]
    
    @property
    def author_premium(self):
        return self.data["author_premium"]

    @property
    def subreddit(self):
        return self.data["subreddit"]
    @property
    def subreddit_id(self):
        return self.data["subreddit"]

    @property
    def subreddit_subscribers(self):
        return self.data["subreddit_subscribers"]
    
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
    def selftext(self):
        return self.data["selftext"]
    
    @property
    def num_comments(self):
        return self.data["num_comments"]
    
    @property
    def total_awards_received(self):
        return self.data["total_awards_received"]
    
    @property
    def all_awardings(self):
        return self.data["all_awardings"]
    
    @property
    def view_count(self):
        return self.data["view_count"]
    
    @property
    def permalink(self):
        return self.data["permalink"]
    
    @property
    def url(self):
        return self.data["url"]
    
    @property
    def created(self, datetime=False):
        return self._handle_timestamp(self.data["created"]) if datetime == True else self.data["created"]
    
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
