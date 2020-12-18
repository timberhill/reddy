import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from datetime import datetime
from modules import PushshiftAPI, RedditAPI, load_posts


#  [r/askreddit] 12.7% Posts: 995.5k. Oldest: 2020-02-06 09:24:07. ETA: 65h 41m 21s

#  [r/teenagers] ... Oldest: 2019-07-21 17:05:12. ETA: 86h 9m 9s

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("No subreddits specified as commandline arguments. Exiting.")
        exit()
    elif len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
        subreddits = open(sys.argv[1], "r").read().split("\n")
        subreddits = [x for x in subreddits if x != "" and x.strip()[0] != "#"] # remove empty
    else:
        subreddits = sys.argv[1:]

    daterange = [
        datetime(2020, 11, 24, 0, 0, 0).timestamp(),
        datetime(2016, 1, 1, 0, 0, 0).timestamp(),
    ]

    papi = PushshiftAPI()
    rapi = RedditAPI()

    for subreddit in subreddits:
        load_posts(subreddit, daterange, papi, rapi)
