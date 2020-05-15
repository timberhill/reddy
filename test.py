import numpy as np
from datetime import datetime, timedelta
from progressbar import ProgressBar, SimpleProgress, ETA
import matplotlib.pyplot as plt
from modules.reddit_api import RedditAPI
from modules.cache_handler import Cache
from credentials import client_id, secret

api   = RedditAPI()
cache = Cache(verbose=False)

api.authenticate(client_id, secret)

stamp_from = 1575158400
stamp_to   = 1577836799

# todo : test https://github.com/peoplma/subredditarchive/blob/master/subredditarchive.py