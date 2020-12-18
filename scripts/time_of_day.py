#!/usr/bin/env python
# coding: utf-8

import sys, os
sys.path.append(os.path.join(os.path.abspath(''), ".."))
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from modules import PushshiftAPI, RedditAPI, DataContext
from modules import load_posts, TimeBin, TimeOfDayBin


if len(sys.argv) != 2:
    raise ValueError("Please specify the subreddit name as one command-line argument")

# subreddit to analyse
subreddit_name = sys.argv[1]

# date range to download
daterange = [
    datetime.now().timestamp(),
    (datetime.now() - timedelta(days=120)).timestamp(),
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

bin_structure = list(TimeOfDayBin.comments(
    posts,
    binsize = timedelta(hours=1),
    step    = timedelta(hours=0.1),
    per_post=True
))

colours = (
    "#F06543",
    "#F07347",
    "#F0814A",
    "#F08F4E",
    "#F09D51",
    "#628B48",
    "#7EA172",
)

f, ax = plt.subplots(7, 1, sharex=True, sharey=True, figsize=(10, 6))
i = 0
for t, v in bin_structure:
    ax[i].step(t, v, c=colours[i], where="post")
    i += 1
plt.show()
