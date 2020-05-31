from collections.abc import Iterable
import os
import glob
import json
import pandas as pd
from datetime import datetime, timezone

from .containers import RedditPost


class Cache(object):
    """
    Saves, retrieves and indexes the downloaded reddit posts.
    """
    def __init__(self, basepath="../data", cores=1, verbose=False, output_function=print):
        self.basepath = basepath
        self.cores = cores
        self.output_function = output_function
        self.verbose = verbose

    
    @property
    def _headers(self):
        return [
            "post_id",
            "author",
            "subreddit_subscribers",
            "title",
            "downs",
            "ups",
            "num_comments",
            "total_awards_received",
            "view_count",
            "created",
            "created_utc",
            "permalink",
        ]


    def where(self, subreddit, t=None, tolerance=1):
        """
        Retrieve the posts from the cache.

        subreddit, str: subreddit name.

        t, int/float/datetime/tuple: time or list of times as unix time or python datetime object in UTC (optional)

        tolerance, int: tolerance for the time/date if only one number is specified, in seconds (default: 10 seconds)
        """
        if not self._index_exists(subreddit):
            raise FileNotFoundError(f"Could not find an index file for r/{subreddit}.")

        index_path = self._get_index_path(subreddit)
        posts = pd.read_feather(index_path, columns=self._headers)

        if t is None:
            return posts

        isnumber   = lambda obj: isinstance(t, int) or isinstance(t, float)
        tounixtime = lambda obj: obj.replace(tzinfo=timezone.utc).timestamp()
        
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
            raise ValueError("Wrong value encountered in cache.select(t=???). Use datetime object or unix time, or a tuple.")
        
        mask = (posts["created_utc"] >= t[0]) & (posts["created_utc"] <= t[1])
        return posts.where(mask).dropna(axis=0, how='any')


    def add(self, posts):
        """
        Add post(s) to the cache (== save the json files)

        data, list/RedditPost: reddit posts ot a list of reddit posts.
        """
        if not isinstance(posts, Iterable):
            posts = [posts,]
        
        subreddits = set([post.subreddit for post in posts])
        
        for subreddit in subreddits:
            subreddit_posts = [post for post in posts if post.subreddit == subreddit]
            index_path = self._get_index_path(subreddit)

            if self._index_exists(subreddit): # get or create a dataframe
                old_dataframe = pd.read_feather(index_path, columns=self._headers)
            else:
                self._create_directory_structure(index_path)
                old_dataframe = pd.DataFrame(data=None, columns=self._headers)

            new_dataframe = pd.concat([
                old_dataframe, 
                pd.DataFrame({
                    "post_id": [post.id for post in subreddit_posts],
                    "author":  [post.author for post in subreddit_posts],
                    "subreddit_subscribers": [post.subreddit_subscribers for post in subreddit_posts],
                    "title":   [post.title for post in subreddit_posts],
                    "downs":   [post.downs for post in subreddit_posts],
                    "ups":     [post.ups for post in subreddit_posts],
                    "num_comments": [post.num_comments for post in subreddit_posts],
                    "total_awards_received": [post.total_awards_received for post in subreddit_posts],
                    "view_count":  [post.view_count for post in subreddit_posts],
                    "created":     [post.created for post in subreddit_posts],
                    "created_utc": [post.created_utc for post in subreddit_posts],
                    "permalink":   [post.permalink for post in subreddit_posts],
                }, columns=self._headers)
            ]).drop_duplicates(['post_id'], keep='last')

            # save to file
            new_dataframe.reset_index().to_feather(index_path)


    def _get_index_path(self, subreddit=None):
        """
        Get a subreddit data file path.

        subreddit, str: subreddit name.
        """
        return os.path.join(self.basepath, subreddit.lower(), "index.feather")
    

    def _index_exists(self, subreddit):
        """
        Check if the index file exists.
        """
        return os.path.isfile(self._get_index_path(subreddit))


    def _create_directory_structure(self, path):
        """
        Create directory structure for specified path.
        """
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
