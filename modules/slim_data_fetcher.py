from .datacontext import DataContext
from .bin import TimeBin
from datetime import timedelta, datetime
from pandas import concat


class SlimDataFetcher(object):
    """
    A helper class for large data sets, designed to avoid memory errors.
    
    E.g. use this instead of DataContext to load posts of big subreddits like r/AskReddit.
    """
    @staticmethod
    def fetch(subreddit_name, daterange, utc=False, chunk_size=30, include_removed=False):
        """
        something something bit ny bit

        """
        columns_to_save = [
            "created",
            "created_utc",
            "ups",
            "upvote_ratio",
            "num_comments"
        ]

        if daterange[0] < daterange[1]:
            daterange = [daterange[1], daterange[0]]
        
        chunk_size_seconds = timedelta(days=chunk_size).total_seconds()

        slim_posts = None
        temp_range = [daterange[0], daterange[0]-chunk_size_seconds]
        with DataContext() as context:
            while temp_range[0] > daterange[1]:
                if temp_range[1] < daterange[1]:
                    temp_range[1] = daterange[1]

                posts_chunk = context.select_posts(
                    subreddit_name=subreddit_name,
                    include_removed=include_removed,
                    daterange=(temp_range[1], temp_range[0]),
                    pandas=True
                )

                if slim_posts is None:
                    slim_posts = posts_chunk[columns_to_save]
                else:
                    slim_posts = concat([slim_posts, posts_chunk[columns_to_save]])
                
                temp_range[0] -= chunk_size_seconds
                temp_range[1] -= chunk_size_seconds
                
                print(f"Fetched: {len(slim_posts)} slim posts")
        
        return slim_posts
