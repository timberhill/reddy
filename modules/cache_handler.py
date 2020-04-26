from collections.abc import Iterable
import os
import glob
import json
import pandas as pd

from .containers import RedditPost


class Cache(object):
    """
    Saves, retrieves and indexes the downloaded reddit posts.
    """
    def __init__(self, folder="data", cores=1, verbose=False, output_function=print):
        self.folder = folder
        self.cores = cores
        self.output_function = output_function
        self.verbose = verbose
    

    def select(self, subreddit, datetime=None, utc=True):
        """
        Retrieve the posts from the cache.

        subreddit, str: subreddit name.

        datetime, int/float/datetime/tuple: time or list of times as unix time or python datetime object (optional)

        utc, bool: is time parameter specified in UTC (default: True)
        """
        raise NotImplementedError
    

    def update_index(self, subreddit):
        """
        Update the index file for a subreddit
        """
        raise NotImplementedError
        

    def update_all_indices(self, subreddit):
        """
        Update all the index files.
        """
        raise NotImplementedError


    def add(self, data, overwrite=False):
        """
        Add post(s) to the cache (== save the json files)

        data, list/RedditPost: reddit posts ot a list of reddit posts.

        update, bool: overwrite existing files witht the new data or not (defult: False)
        """
        if not isinstance(data, Iterable):
            data = [data,]
        
        for post in data:
            if not isinstance(post, RedditPost):
                raise ValueError("'data' argument in Cache.add() must be a RedditPost instance or a list of RedditPost instances.")

            dump = json.dumps(post.data, sort_keys=True, indent=4)
            path = self._get_json_path(post)
            older_file_exists = os.path.isfile(path)

            if older_file_exists:
                # file already exists
                if overwrite == False:
                    # we don't overwrite it
                    if self.verbose:
                        self.output_function(f"Already exists: r/{post.subreddit}/{post.id}.")
                    continue

            # write to the file
            self._create_directory_structure(path)
            with open(path, "w") as f:
                f.write(dump)
            
            if self.verbose and older_file_exists:
                self.output_function(f"Overwritten r/{post.subreddit}/{post.id}.")
            
            if self.verbose and not older_file_exists:
                self.output_function(f"Saved r/{post.subreddit}/{post.id}.")
    

    def _get_json_path(self, post=None, subreddit=None, post_id=None):
        """
        Generate path for a post.

        Specify weither a post instance, or a subreddit/post_id pair

        post, RedditPost: the post intended to be saved.

        subreddit, str: subreddit name.

        post_id, str: ID of the reddit post.
        """
        if post is not None:
            subreddit = post.subreddit
            post_id   = post.id
        
        if subreddit is None or post_id is None:
            raise ValueError("Specify either a post instance, or a subreddit/post_id pair in Cache._get_json_path()")

        return os.path.join(self.folder, subreddit, "json", f"{post_id}.json")


    def _create_directory_structure(self, path):
        """
        Create directory structure for specified path.
        """
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))