import json
import requests
import warnings
from datetime import datetime, timedelta

from .containers import RedditPost


class RedditAPI(object):
    """
    Simple wrapper for some Reddit API.
    See https://www.reddit.com/dev/api
    """
    def __init__(self):
        self._access_token = None
        self._access_token_deadline = None

        self._client_id = None
        self._secret    = None


    def _headers(self):
        header = { "User-Agent": "python:reddy:v0.1 (by /u/timberhilly)" }
        if self._access_token is not None:
            header["Authorization"] = f"bearer {self._access_token}"

        return header


    def authenticate(self, client_id, secret, scope="read"):
        """
        OAuth2, see https://github.com/reddit-archive/reddit/wiki/OAuth2
        """
        # following this example:
        # https://github.com/reddit-archive/reddit/wiki/OAuth2-Python-Example
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
            
            self._client_id = client_id
            self._secret = secret
        else:
            raise KeyError("'access_token' was not returned by the server.")


    def verify_authentication(self):
        time_now = datetime.utcnow()
        if time_now >= self._access_token_deadline:
            # token expired, get a new one
            self.authenticate(self._client_id, self._secret)


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
