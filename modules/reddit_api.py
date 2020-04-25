import json
import requests
import warnings


class RedditAPI(object):
    """
    Simple wrapper for some Reddit API.

    See https://www.reddit.com/dev/api
    """
    def __init__(self):
        self.current_before = None
        self.current_after = None
    

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
    
    def new_posts(self, subreddit, before=None, after=None, limit=100):
        """
        Returns posts sorted by new.

        subreddit, str: name of the subreddit.
        before, str:    ID of the previous page
        after, str:     ID of the next page
        limit, int:     number of posts to return (1-100)
        """
        before, after, limit = self._validate_paging_arguments(before, after, limit)
        base_url = f"https://www.reddit.com/r/{subreddit}/new.json"

        response = requests.get(base_url, dict(
            before=before,
            after=after,
            limit=limit
        ))
        response.raise_for_status()
        response_dictionary = json.loads(response.content)

        print(response_dictionary)
