from datetime import datetime

class RedditPost(object):
    def __init__(self, subreddit="", title="", 
        downs=0, ups=0, total_awards_received=0, author_premium=False, 
        created=0.0, view_count=0, id=0, permalink="", url="", created_utc=0):
        
        self.subreddit = subreddit
        self.subreddit = subreddit
        self.title = title
        self.downs = downs
        self.ups = ups
        self.total_awards_received = total_awards_received
        self.author_premium = author_premium
        self.view_count = view_count
        self.id = id
        self.permalink = permalink
        self.url = url

        self.created = self._handle_timestamp(created)
        self.created_utc = self._handle_timestamp(created_utc)


    def _handle_timestamp(self, value):
        if type(value) is isinstance(value, datetime):
            return value
        elif type(value) is float or type(value) is int:
            return datetime.fromtimestamp(value)
        else:
            raise ValueError(f"Invalid time format/value encountered: {value}.")


    @classmethod
    def from_json(cls, data):
        if type(data) is not dict:
            import json
            data = json.loads(data)
            
        return cls(
            subreddit=data["subreddit"],
            title=data["title"],
            downs=data["downs"],
            ups=data["ups"],
            total_awards_received=data["total_awards_received"],
            author_premium=data["author_premium"],
            created=data["created"],
            view_count=data["view_count"],
            id=data["id"],
            permalink=data["permalink"],
            url=data["url"],
            created_utc=data["created_utc"]
        )
