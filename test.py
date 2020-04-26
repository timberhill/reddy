from modules.reddit_api import RedditAPI
from modules.cache_handler import Cache
from credentials import client_id, secret

api = RedditAPI()
cache = Cache(verbose=True)

api.authenticate(client_id, secret)

# after = None
# count = 0
# for i in range(100):
#     posts, before, after = api.new_posts("datascience", limit=100, after=after, count=count)
#     count += len(posts)
#     print(f"req{i} : {count}")
#     cache.add(posts, overwrite=False)

cache.update_all_indices()
