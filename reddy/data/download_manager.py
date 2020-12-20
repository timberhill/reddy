"""
"""
from datetime import datetime
from datetime import timedelta
import time

from .datacontext import DataContext
from ..api.pushshift_api import PushshiftAPI
from ..api.reddit_api import RedditAPI
from ..utilities.logger import Logger
from ..utilities.shared import time_to_unix
from ..utilities.shared import time_to_hms

LOGGER = Logger()


class RedditDownloadManager:
    """
    """

    def __init__(self, retries=5, wait=5, progress=True, skip_time=3600):
        self.retries = retries
        self.wait = wait
        self.progress = progress
        self.skip_time = skip_time

        self._datacontext = DataContext()
        self._reddit = RedditAPI()
        self._pushshift = PushshiftAPI()

        LOGGER.debug("Created RedditDownloadManager instance")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._datacontext.close()
        LOGGER.debug(
            f"Closed RedditDownloadManager instance ({exc_type})")

    def _send_request(self, request_function):
        """
        """
        retry = 0
        while retry <= self.retries:
            LOGGER.debug(f"Sending a request, try {retry} of {self.retries}")
            try:
                return request_function()
            except Exception as e:
                retry += 1
                if retry <= self.retries:
                    LOGGER.warn(
                        f"API request failed (try {retry} of {self.retries}," +
                        f"retrying in {self.wait}s): {e}.")
                    time.sleep(wait)
                else:
                    LOGGER.warn(
                        f"API request failed (try {retry} of {self.retries}): {e}.")

    def download_posts(self, subreddit,
                       start=datetime.utcnow(),
                       end=datetime.utcnow()-timedelta(days=7),
                       progress=True):
        """
        """
        if progress:
            LOGGER.info(f"Starting posts download from r/{subreddit}")

        start = time_to_unix(start)
        end = time_to_unix(end)

        progress_start = datetime.utcnow()
        progress_timerange = start - end
        progress_posts_loaded = 0

        # start the actual download process:
        # 1. download 500 post IDs from PushShift (max limit)
        # 2. split the list into 100-post chunks (reddit api limit)
        # 3.   download post data for each chunk from reddit api
        # 4.   save to the database
        oldest_epoch = start
        while oldest_epoch > end:
            # load 500 post IDs from pushshift
            ps_posts = self._send_request(
                lambda: self._pushshift.search(
                    subreddit, before=int(oldest_epoch), limit=500)
            )

            ps_nposts = 0 if ps_posts is None else len(ps_posts)
            LOGGER.debug(f"Pushshift API: fetched {ps_nposts}.")

            if ps_posts is None or len(ps_posts) == 0:
                # no posts in this timerange
                # move on by 'self.skip_time' seconds
                oldest_epoch += self.skip_time
                continue

            # prepare post ID subsets for reddit API
            # by splitting them into chunks with 100 IDs each
            ids = [f"t3_{post.id}" for post in ps_posts]
            n = 100  # number of post ids per request (reddit api limitation)
            id_subsets = [ids[i*n: (i+1)*n] for i in range((len(ids)+n-1)//n)]

            # load the posts from Reddit API
            for i, subset in enumerate(id_subsets):
                posts = self._send_request(
                    lambda: self._reddit.info(subreddit, subset)
                )

                nposts = 0 if posts is None else len(posts)
                LOGGER.debug(f"Reddit API: fetched {nposts}. " +
                             "Request # {i}, PS posts: {ps_nposts}).")

                if posts is None:
                    continue

                LOGGER.debug(f"Adding {nposts} posts to the database.")
                self._datacontext.add_posts(posts)

                # move the current oldest epoch to the oldest post here
                oldest_epoch = min([post.created_utc for post in posts])

                if progress:
                    progress_posts_loaded += len(posts)
                    loaded_timerange = start - oldest_epoch
                    time_since_start = datetime.utcnow() - progress_start
                    load_rate = loaded_timerange / time_since_start.total_seconds()
                    percentage = 100.0 * loaded_timerange / progress_timerange

                    eta = (progress_timerange - loaded_timerange) / load_rate
                    h, m, s = time_to_hms(eta)

                    LOGGER.info(
                        f"Fetched {progress_posts_loaded/1000:.1f}k posts, " +
                        f"Oldest: {datetime.fromtimestamp(oldest_epoch)}, " +
                        f"Progress: {percentage:.1f}%, " +
                        f"ETA: {h:0.0f}h {m:0.0f}m {s:0.0f}s"
                    )

            LOGGER.debug(f"Committing changes to the database.")
            self._datacontext.commit()
