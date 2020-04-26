from modules.reddit_api import RedditAPI
from modules.cache_handler import Cache
from credentials import client_id, secret

api = RedditAPI()

api.authenticate(client_id, secret)

posts, before, after = api.new_posts("analog", limit=10)

cache = Cache(verbose=False)
cache.add(posts, overwrite=False)
