from datetime import datetime, timedelta
import threading
import time

from . import DataContext

def time_to_unix(value):
    """
    Returns unix time or time difference in seconds.
    """
    if isinstance(value, datetime):
        return value.timestamp()
    elif isinstance(value, timedelta):
        return value.total_seconds()
    elif type(value) is float or type(value) is int:
        return value
    else:
        raise ValueError(f"Invalid time format/value encountered: {value}.")


def load_newest_posts(subreddit_name, rapi, cache, n=1000):
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
    oldest_epoch = epochrange[0]
    while oldest_epoch > epochrange[1]:
        posts = papi.search(subreddit_name, before=int(oldest_epoch), limit=500)
        oldest_epoch = min([post.created_utc for post in posts])
        ids += [post.id for post in posts]

    return ids


def send_request(request_function, retries=3, ignore_errors=False, wait=10):
    retry = 0
    result = None
    while retry <= retries:
        try:
            result = request_function()
            break
        except Exception as e:
            retry += 1
            if not ignore_errors and retry == retries:
                print(f"\nError occured in API request:\n{e}\nSkipping.")
            elif not ignore_errors and retry <= retries:
                print(f"\nError occured in API request:\n{e}\nRetrying in {wait}s...")
                time.sleep(wait)

    return result


def load_posts(subreddit_name, epochrange, papi, rapi, progress=True):
    """
    Load post IDs between dates using Pushshift API and then load full info from Reddit API.

    papi, PushshiftAPI: Pushshift API client object,

    rapi, RedditAPI: reddit API client object,

    subreddit_name, str: subredit name to load posts from,

    epochrange, tuple: 'from' and 'to' epochs in unix time.

    """
    if progress:
        print(f"Downloading posts from r/{subreddit_name}...", end="\r")

    # for the progress:
    start = datetime.utcnow()
    posts_loaded = 0
    full_range = datetime.fromtimestamp(epochrange[0]) - datetime.fromtimestamp(epochrange[1])

    with DataContext() as datacontext:
        ids = []
        epoch_diff = 3600 # how much unix time (seconds) to skip if the API is stuck
        oldest_epoch = epochrange[0]
        while oldest_epoch > epochrange[1]:
            # load the IDs
            ps_posts = send_request(
                lambda: papi.search(subreddit_name, before=int(oldest_epoch), limit=500),
                retries=5,
                ignore_errors=True
            )

            if ps_posts is None or len(ps_posts) == 0:
                oldest_epoch += epoch_diff
                continue

            ps_created_utc = [post.created_utc for post in ps_posts]
            # epoch_diff = max(ps_created_utc) - min(ps_created_utc)

            # prepare post ID subsets for reddit API
            ids = [f"t3_{post.id}" for post in ps_posts]
            n = 100 # number of post ids per request (redit api limitation)
            id_subsets = [ids[i*n : (i+1)*n] for i in range((len(ids)+n-1)//n)]

            # load the posts from Reddit API
            for i, subset in enumerate(id_subsets):
                posts = send_request(
                    lambda: rapi.info(subreddit_name, subset),
                    retries=5,
                    ignore_errors=True
                )
                if posts is None:
                    continue

                datacontext.add_posts(posts)
                
                oldest_epoch = min([post.created_utc for post in posts])
                posts_loaded += len(posts)
                    
                if progress:
                    # calculate ETA
                    loaded_range = datetime.fromtimestamp(epochrange[0]) - datetime.fromtimestamp(oldest_epoch)
                    time_since_start = datetime.utcnow() - start
                    load_rate = loaded_range.total_seconds() / (time_since_start.total_seconds()) # seconds of posts downloded per second
                    percentage = 100.0 * loaded_range.total_seconds() / full_range.total_seconds()
                    eta_sec = (full_range - loaded_range).total_seconds() / load_rate
                    m, s = divmod(eta_sec, 60)
                    h, m = divmod(m, 60)

                    print(
                        f" [r/{subreddit_name.lower()}] " + \
                        f"{percentage:.1f}% " + \
                        f"Posts: {posts_loaded/1000:.1f}k. " + \
                        f"Oldest: {datetime.fromtimestamp(oldest_epoch)}. " + \
                        f"ETA: {h:0.0f}h {m:0.0f}m {s:0.0f}s    ",
                    end='\r')

            datacontext.commit()

        timeused = time_since_start.total_seconds()
        m, s = divmod(timeused, 60)
        h, m = divmod(m, 60)
        print(
            f"[r/{subreddit_name}] " + \
            f"Downloaded {posts_loaded} posts in {h:0.0f}h {m:0.0f}m {s:0.0f}s                                    "
        )