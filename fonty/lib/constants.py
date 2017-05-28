'''constants.py'''

import os
from appdirs import user_data_dir

APP_NAME = 'fonty'
APP_DIR = user_data_dir(APP_NAME)
SEARCH_INDEX_PATH = os.path.join(APP_DIR, 'index')
SUBSCRIPTIONS_PATH = os.path.join(APP_DIR, 'subscriptions.json')