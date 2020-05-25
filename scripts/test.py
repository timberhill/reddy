import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

from modules import PushshiftAPI, RedditAPI, Cache
from modules import load_posts, plot_submission_frequency_histogram_2020


if __name__ == "__main__":

    subreddit_name = "skyrim"
    daterange = [
        datetime(2020, 5, 1, 0, 0, 0).timestamp(), # 
        datetime(2020, 1, 1, 0, 0, 0).timestamp()
    ]

    cache = Cache(verbose=False)
    papi  = PushshiftAPI()
    rapi  = RedditAPI()

    # cache.update_index(subreddit_name)
    # load_posts(subreddit_name, daterange, papi, rapi, cache)
    posts = cache.where(subreddit_name, t=None)

    f, ax = plot_submission_frequency_histogram_2020(f"Posts from r/{subreddit_name}", posts, upvote_limits=[0, 100])
    plt.show()
