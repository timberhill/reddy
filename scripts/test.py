import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime
from modules import PushshiftAPI, RedditAPI, Cache
from modules import plot_submission_frequency_histogram, show_progress
from credentials import client_id, secret


def load_newest_posts(rapi, subreddit_name, n=1000):
    """
    Load latest 100 posts using Redit API.

    rapi, RedditAPI: reddit API client object,

    subreddit_name, str: subredit name to load posts from,

    Returns:
        oldest post epoch, unix time
    """
    after, count = None, 0
    epochs = []
    for i in range(int(n / 100)):
        posts, before, after = rapi.new_posts(subreddit_name, limit=100, after=after, count=count)
        cache.add(posts, overwrite=True)
        count += len(posts)
        epochs += [post.created_utc for post in posts]

    cache.update_index(subreddit_name)

    return min(epochs)


def load_pushshift_post_ids(papi, subreddit_name, epochrange):
    """
    Load post IDs between dates using Pushshift API.

    papi, PushshiftAPI: Pushshift API client object,

    subreddit_name, str: subredit name to load posts from,

    epochrange, tuple: 'from' and 'to' epochs in unix time.

    Returns:
        list of post IDs
    """
    ids = []
    oldest_epoch = epochrange[1]
    while oldest_epoch > final_epoch:
        posts = papi.search(subreddit_name, before=int(oldest_epoch), limit=500)
        oldest_epoch = min([post.created_utc for post in posts])
        ids += [post.id for post in posts]

    return ids


def load_posts(subreddit_name, epochrange, papi, rapi, cache, progress=True):
    """
    Load post IDs between dates using Pushshift API and then load full info from Reddit API.

    papi, PushshiftAPI: Pushshift API client object,

    rapi, RedditAPI: reddit API client object,

    subreddit_name, str: subredit name to load posts from,

    epochrange, tuple: 'from' and 'to' epochs in unix time.

    """
    ids = []
    oldest_epoch = epochrange[0]
    while oldest_epoch > epochrange[1]:
        # load the IDs
        posts = papi.search(subreddit_name, before=int(oldest_epoch), limit=500)
        oldest_epoch = min([post.created_utc for post in posts])
        ids = [f"t3_{post.id}" for post in posts]

        # divide the posts into chunks of 100
        n = 100 # number of post ids per request (redit api limitation)
        id_subsets = [ids[i*n : (i+1)*n] for i in range((len(ids)+n-1)//n)]

        # load the posts
        for subset in id_subsets:
            posts = rapi.info(subreddit_name, subset)
            cache.add(posts, overwrite=True)

            if progress:
                t = datetime.fromtimestamp(min([post.created_utc for post in posts]))
                print(f"Loaded {len(posts)} posts, oldest: {t}")

            # show_progress(
            #     i=min([post.created_utc for post in posts]) - epochrange[0],
            #     n=epochrange[1] - epochrange[0]
            # )

    cache.update_index(subreddit_name)


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np

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

    f, ax = plot_submission_frequency_histogram(f"Posts from r/{subreddit_name}", posts, upvote_limits=[0, 10, 100], bins=np.arange(-400, 200, 7))
    plt.show()

