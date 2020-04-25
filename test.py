from modules.reddit_api import RedditAPI
from credentials import client_id, secret

api = RedditAPI()

api.authenticate(client_id, secret)

posts, before, after = api.new_posts("analog", limit=10)

for post in posts:
    print(post.title)
