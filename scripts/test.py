import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import numba
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from modules import DataContext, Bin


if __name__ == "__main__":
    subreddit_name = sys.argv[1] if len(sys.argv) == 2 else "skyrim"

    daterange = [
        datetime.utcnow().timestamp(),
        datetime(2019, 1, 1, 0, 0, 0).timestamp(),
    ]

    print("Fetching... ", end="", flush=True)
    with DataContext() as context:
        posts = context.select_posts(subreddit_name=subreddit_name, include_removed=False)
    print("done")


    print("Binning...  ", end="", flush=True)
    bins, values = Bin.comments(
        posts,
        start   = datetime(2019, 1, 1, 0, 0, 0),
        end     = datetime(2019, 7, 1, 0, 0, 0),
        binsize = timedelta(days=7),
        step    = timedelta(days=1),
        per_post= True
    )
    print("done")
    bins -= bins[0]
    bins /= timedelta(days=30).total_seconds()
    # values = np.array(values) / np.median(values[5:20])
    plt.plot(bins, values)


    print("Binning...  ", end="", flush=True)
    bins, values = Bin.comments(
        posts,
        start   = datetime(2020, 1, 1, 0, 0, 0),
        end     = datetime(2020, 7, 1, 0, 0, 0),
        binsize = timedelta(days=7),
        step    = timedelta(days=1),
        per_post= True
    )
    print("done")
    bins -= bins[0]
    bins /= timedelta(days=30).total_seconds()
    # values = np.array(values) / np.median(values[5:20])
    plt.plot(bins, values)


    plt.show()
