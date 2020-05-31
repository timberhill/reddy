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
        posts = pd.read_csv(index_path, header=0, sep=",")

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


    def _load_json_file(self, path):
        with open(path, "r") as f:
            data = json.load(f)
        return data


    def update_index(self, subreddit):
        """
        Update the index file for a 
        
        subreddit, str: subreddit name
        """
        index_path     = os.path.join(self.basepath, subreddit.lower(), "index.txt")
        json_folder    = os.path.join(self.basepath, subreddit.lower(), "json")
        json_filenames = [filename for filename in os.listdir(json_folder) if filename.endswith(".json")]
        json_data      = [self._load_json_file(os.path.join(json_folder, filename)) for filename in json_filenames]

        entries = [
            f'\n{post["id"]},{post["created"]},{post["created_utc"]},{post["ups"]},{post["downs"]},{post["view_count"]}'
            for post in json_data
        ]
        entries.insert(0, "post_id,created,created_utc,ups,downs,view_count")

        # write to file
        with open(index_path, "w") as index:
            for entry in entries:
                index.write(entry)
        
        if self.verbose:
            self.output_function(f"Updated index for r/{subreddit} ({len(json_filenames)} posts).")


    def update_all_indices(self):
        """
        Update all the index files.
        """
        subreddits = os.listdir(self.basepath)

        # TODO : implement parallel execution?
        for subreddit in subreddits:
            self.update_index(subreddit)


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

            path = self._get_json_path(post)
            older_file_exists = os.path.isfile(path)
            if older_file_exists: # file already exists
                if overwrite == False: # we don't overwrite it
                    if self.verbose:
                        self.output_function(f"Already exists: r/{post.subreddit}/{post.id}.")
                    continue

            # write to the file
            self._create_directory_structure(path)
            dump = json.dumps(post.data, sort_keys=True, indent=4)
            with open(path, "w") as f:
                f.write(dump)
            
            # announce the results
            if self.verbose and older_file_exists:
                self.output_function(f"Overwritten r/{post.subreddit}/{post.id}.")
            
            if self.verbose and not older_file_exists:
                self.output_function(f"Saved r/{post.subreddit}/{post.id}.")


    def _get_json_folder(self, subreddit=None):
        """
        Get a subreddit json storage folder path.

        Specify weither a post instance, or a subreddit/post_id pair

        subreddit, str: subreddit name.
        """
        return os.path.join(self.basepath, subreddit.lower(), "json")
    

    def _get_index_path(self, subreddit=None):
        """
        Get a subreddit json storage folder path.

        Specify weither a post instance, or a subreddit/post_id pair

        subreddit, str: subreddit name.
        """
        return os.path.join(self.basepath, subreddit.lower(), "index.txt")
    

    def _get_json_path(self, post=None, subreddit=None, post_id=None):
        """
        Get a path for the post.

        Specify either a post instance, or a subreddit/post_id pair

        post, RedditPost: the post intended to be saved.

        subreddit, str: subreddit name.

        post_id, str: ID of the reddit post.
        """
        if post is not None:
            subreddit = post.subreddit
            post_id   = post.id
        
        if subreddit is None or post_id is None:
            raise ValueError("Specify either a post instance, or a subreddit/post_id pair in Cache._get_json_path()")

        return os.path.join(self._get_json_folder(subreddit), f"{post_id}.json")


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