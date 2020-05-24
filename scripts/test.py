import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

from modules import PushshiftAPI, RedditAPI, Cache
from modules import plot_submission_frequency_histogram
from credentials import client_id, secret


if __name__ == "__main__":

    subreddit_name = "skyrim"
    daterange = [
        datetime.utcnow().timestamp(),
        datetime(2019, 1, 1, 0, 0, 0).timestamp()
    ]

    cache = Cache(verbose=False)
    papi  = PushshiftAPI()
    rapi  = RedditAPI()
    rapi.authenticate(client_id, secret)

    # cache.update_index(subreddit_name)
    # load_posts(subreddit_name, daterange, papi, rapi, cache)
    posts = cache.where(subreddit_name, t=None)

    f, ax = plot_submission_frequency_histogram(f"Posts from r/{subreddit_name}", posts, upvote_limits=[0, 10, 100])
    plt.show()
