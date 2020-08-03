#!/usr/bin/env python
# coding: utf-8

import sys, os
sys.path.append(os.path.join(os.path.abspath(''), ".."))
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from modules import PushshiftAPI, RedditAPI, DataContext, SlimDataFetcher
from modules import load_posts, Bin, Plot


if len(sys.argv) != 2:
    raise ValueError("Please specify the subreddit name as one command-line argument")

# subreddit to analyse
subreddit_name = sys.argv[1]

# date range to download
daterange = [
    datetime(2020, 7, 10, 0, 0, 0).timestamp(),
    datetime(2019, 1, 1, 0, 0, 0).timestamp(),
]

columns = [
    "created",
    "created_utc",
    "ups",
    "upvote_ratio",
    "num_comments"
]

update_posts = False

with DataContext() as context:
    posts = context.select_posts(
                subreddit_name=subreddit_name,
                daterange=(daterange[1], daterange[0]),
                columns=columns,
                include_removed=True
            )

# if update_posts or len(posts) == 0:
#     load_posts(subreddit_name, daterange, PushshiftAPI(), RedditAPI(), progress=True)    
#     with DataContext() as context:
#         posts = context.select_posts(subreddit_name=subreddit_name, daterange=daterange, include_removed=False)

print(f"Fetched {len(posts)} posts.")

years = [2020, 2019]
f = plt.figure(figsize=(16, 8))
for year in years:
    t, v = Bin.posts(
        posts,
        start   = datetime(year, 1, 1, 0, 0, 0),
        end     = datetime(year, 12, 31, 23, 59, 59),
        binsize = timedelta(days=7),
        step    = timedelta(days=7)
    )
    Plot.timeseries_yearly(t, v, year, accent=year==2020)

t = f.suptitle(f"r/{subreddit_name}", ha="left")
plt.show()


# TODO: do this for lockdown range:
# https://stackoverflow.com/questions/8500700/how-to-plot-a-gradient-color-line-in-matplotlib
