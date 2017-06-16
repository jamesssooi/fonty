'''constants.py'''

import os
import sys
from appdirs import user_data_dir
from termcolor import colored

# Paths
APP_NAME = 'fonty'
APP_DIR = user_data_dir(APP_NAME)
ROOT_DIR = os.getcwd()
SEARCH_INDEX_PATH = os.path.join(APP_DIR, 'index')
SUBSCRIPTIONS_PATH = os.path.join(APP_DIR, 'subscriptions.json')

# Colors
COLOR_OK = 'green'
COLOR_ERR = 'red'
COLOR_INPUT = 'cyan'

# Action statuses
ACTION_OK = colored('✓', COLOR_OK)
ACTION_ERR = colored('✗', COLOR_ERR)

# System
IS_x64 = sys.maxsize > 2**32
