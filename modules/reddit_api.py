import json
import requests
import warnings
from datetime import datetime, timedelta
from collections.abc import Iterable

from .containers import RedditPost


class RedditAPI(object):
    """
    Simple wrapper for some Reddit API.
    See https://www.reddit.com/dev/api

    NOTE: If you're using this service outside the code in github.com/timberhill/reddy, please use your own API credentials.

    client_id, str: Reddit API client ID, optional

    secret, str: Reddit API client secret, optional
    """
    def __init__(self, client_id=None, secret=None):
        self._access_token = None
        self._access_token_deadline = None

        self.authenticate(client_id, secret)


    def _headers(self):
        header = { "User-Agent": "python:reddy:v0.1 (by /u/timberhilly)" }
        if self._access_token is not None:
            header["Authorization"] = f"bearer {self._access_token}"

        return header


    def authenticate(self, client_id=None, secret=None, scope="read"):
        """
        OAuth2, see https://github.com/reddit-archive/reddit/wiki/OAuth2

        NOTE: If you're using this service outside the code in github.com/timberhill/reddy, please use your own API credentials.

        client_id, str: Reddit API client ID, optional

        secret, str: Reddit API client secret, optional

        scope, str: API scope, default: "read"
        """
        if client_id is None or secret is None:
            from cryptography.fernet import Fernet
            with \
                open("../modules/bin/62608e08adc29a8d6dbc9754e659f125", "rb") as a, \
                open("../modules/bin/3c6e0b8a9c15224a8228b9a98ca1531d", "rb") as b, \
                open("../modules/bin/5ebe2294ecd0e0f08eab7690d2a6ee69", "rb") as c:
                f = Fernet(b.read()[4:-3])
                ab, cb = f.decrypt(a.read()[4:-3]), f.decrypt(c.read()[4:-3])
        
        # following this example:
        # https://github.com/reddit-archive/reddit/wiki/OAuth2-Python-Example
        client_id = client_id if client_id is not None else ab.decode("utf-8")
        secret = secret if secret is not None else cb.decode("utf-8")
        client_auth = requests.auth.HTTPBasicAuth(client_id, secret)
        post_data = {
            "grant_type":   "client_credentials",
            "user":         client_id, 
            "password":     secret, 
            "scope":        scope,
            "redirect_uri": "https://github.com/timberhill/reddy"
        }

        response = requests.post(
            "https://ssl.reddit.com/api/v1/access_token",
            auth=client_auth,
            data=post_data,
            headers=self._headers()
        )
        
        response_dictionary = json.loads(response.content)
        if "access_token" in response_dictionary:
            self._access_token = response_dictionary["access_token"]
            self._access_token_deadline = \
                datetime.utcnow() \
                + timedelta(seconds=response_dictionary["expires_in"])
        else:
            raise KeyError("'access_token' was not returned by the server.")


    def verify_authentication(self):
        time_now = datetime.utcnow()
        if time_now >= self._access_token_deadline:
            # token expired, get a new one
            self.authenticate()


    def _validate_paging_arguments(self, before, after, limit):
        if before is not None and after is not None:
            raise ValueError("Please specify either 'before' or 'after', not both.")

        if limit < 1:
            warnings.warn(f"Silly value encountered in parameter 'limit' ({limit}), setting it to 1.")
            limit = 1
            
        if limit > 100:
            warnings.warn(f"Reddit API does not return more than 100 posts, but 'limit' was set to {limit}, using value of 100 instead.")
            limit = 100
        
        return before, after, limit


    def new_posts(self, subreddit, limit=100, before=None, after=None, count=None):
        """
        Returns posts sorted by new.

        subreddit, str: name of the subreddit.

        before, str:    ID of the previous page

        after, str:     ID of the next page

        limit, int:     number of posts to return (1-100)
        """
        self.verify_authentication()
        before, after, limit = self._validate_paging_arguments(before, after, limit)
        base_url = f"https://oauth.reddit.com/r/{subreddit}/new"
        
        response = requests.get(base_url, dict(
            before=before,
            after=after,
            limit=limit,
            count=count,
        ), headers=self._headers())

        response.raise_for_status()
        response_dictionary = json.loads(response.content)
        posts = [RedditPost.from_json(post["data"]) for post in response_dictionary["data"]["children"]]
        
        return posts, response_dictionary["data"]["before"], response_dictionary["data"]["after"]


    def search(self, subreddit, query, limit=100, before=None, after=None, count=None):
        """
        Search API client.

        Can be used to load all 

        subreddit, str: name of the subreddit.

        query, str:     search query

        before, str:    ID of the previous page

        after, str:     ID of the next page

        limit, int:     number of posts to return (1-100)
        """
        self.verify_authentication()
        before, after, limit = self._validate_paging_arguments(before, after, limit)
        base_url = f"https://oauth.reddit.com/r/{subreddit}/search"
        
        response = requests.get(base_url, dict(
            q=query,
            sort="new",
            syntax="cloudsearch",
            t="all",
            raw_json=1,
            before=before,
            after=after,
            limit=limit,
            count=count,
        ), headers=self._headers())

        response.raise_for_status()
        response_dictionary = json.loads(response.content)
        posts = [RedditPost.from_json(post["data"]) for post in response_dictionary["data"]["children"]]
        return posts, before, after
    

    def info(self, subreddit, item, url=None):
        """
        Retrieve info on a post/comment/subreddit, see https://www.reddit.com/dev/api/#GET_api_info

        Fullnames info: https://www.reddit.com/dev/api/#fullnames (subreddits start with 't3_')

        subreddit, str: name of the subreddit.

        item, str/list:  a comma-separated list of thing fullnames

        url, str: a valid URL
        """
        self.verify_authentication()
        
        if isinstance(item, Iterable):
            item = ",".join(item)

        if len(item.split(",")) > 100 or len(item.split(",")) == 0:
            raise ValueError("Reddit API /r/[subreddit]/api/info can only return between 0 and 100 items per request.")

        base_url = f"https://oauth.reddit.com/r/{subreddit}/api/info"
        response = requests.get(base_url, dict(
            id=item,
            url=url
        ), headers=self._headers())

        response.raise_for_status()
        response_dictionary = json.loads(response.content)

        posts = [RedditPost.from_json(post["data"]) for post in response_dictionary["data"]["children"]]
        return posts