import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

from modules import PushshiftAPI, RedditAPI, Cache
from modules import load_posts, plot_submission_frequency_histogram_2020, plot_submission_time_histogram


if __name__ == "__main__":

    subreddit_name = "unitedkingdom"

    daterange = [
        datetime.utcnow().timestamp(),
        datetime(2020, 1, 1, 0, 0, 0).timestamp(),
    ]

    cache = Cache(verbose=False)
    papi  = PushshiftAPI()
    rapi  = RedditAPI()

    load_posts(subreddit_name, daterange, papi, rapi, cache)

    posts = cache.where(subreddit_name, t=None)

    f, ax = plot_submission_time_histogram(f"Posts from r/{subreddit_name}", posts, success_score=50)
    plt.show()

    f, ax = plot_submission_frequency_histogram_2020(f"Posts from r/{subreddit_name}", posts, upvote_limits=[0, 50])
    plt.show()
