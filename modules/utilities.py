from datetime import datetime
import time

from . import DataContext


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


def send_request(request_function, retries=3, progress=True, wait=30):
    retry = 0
    result = None
    while retry <= retries:
        try:
            result = request_function()
            break
        except Exception as e:
            retry += 1
            if progress and retry == retries:
                print(f"Error occured in API request:\n{e}\n\nSkipping.")
            elif progress and retry <= retries:
                print(f"Error occured in API request:\n{e}\n\nRetrying in {wait}s...")
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
    ids = []
    epoch_diff = 1000
    oldest_epoch = epochrange[0]
    while oldest_epoch > epochrange[1]:
        # load the IDs
        if progress:
            print("> fetching pushshift", end="", flush=True)
        ps_posts = send_request(
            lambda: papi.search(subreddit_name, before=int(oldest_epoch), limit=500),
            retries=5, progress=progress
        )
        if progress:
            print(f" [{len(ps_posts)}]", end="", flush=True)

        if len(ps_posts) == 0:
            oldest_epoch += epoch_diff
            continue

        ps_created_utc = [post.created_utc for post in ps_posts]
        epoch_diff = max(ps_created_utc) - min(ps_created_utc)

        ids = [f"t3_{post.id}" for post in ps_posts]
        n = 100 # number of post ids per request (redit api limitation)
        id_subsets = [ids[i*n : (i+1)*n] for i in range((len(ids)+n-1)//n)]

        # load the posts from Reddit API
        if progress:
            print(f", fetching reddit..", end="", flush=True)
        with DataContext() as datacontext:
            for i, subset in enumerate(id_subsets):
                posts = send_request(
                    lambda: rapi.info(subreddit_name, subset),
                    retries=5, progress=progress
                )
                if progress:
                    print(f".{i+1}", end="", flush=True)

                if posts is None:
                    continue

                datacontext.add_posts(posts)

                oldest_epoch = min([post.created_utc for post in posts])

            datacontext.commit()
            if progress:
                print(f", oldest: {datetime.fromtimestamp(oldest_epoch)}")
