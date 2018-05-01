'''constants.py'''

import os
import sys
import inspect
from typing import Dict, Any
from appdirs import user_data_dir
from termcolor import colored

# Paths
APP_NAME = 'fonty'
APP_DIR = user_data_dir(APP_NAME)
TMP_DIR = os.path.join(APP_DIR, 'tmp')
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(inspect.stack()[0][1])))
SEARCH_INDEX_PATH = os.path.join(APP_DIR, 'index')
SUBSCRIPTIONS_PATH = os.path.join(APP_DIR, 'subscriptions.json')
MANIFEST_PATH = os.path.join(APP_DIR, 'manifest.json')
REPOSITORY_DIR = os.path.join(APP_DIR, 'repositories')

# Filenames
CONFIG_FILENAME = 'fonty.conf'

# URLs
TELEMETRY_ENDPOINT = 'https://analytics.fonty.io/v1'

# Colors
COLOR_OK = 'green'
COLOR_ERR = 'red'
COLOR_INPUT = 'cyan'

# Action statuses
ACTION_OK = colored('✓', COLOR_OK)
ACTION_ERR = colored('✗', COLOR_ERR)

# System
IS_x64 = sys.maxsize > 2**32
IS_WINDOWS = os.name == 'nt'

# Configuration
JSON_DUMP_OPTS: Dict[str, Any] = {'indent': 2, 'separators': (',', ': ')}

# Icons
ICON_WAITING = {
    'WINDOWS': ['|', '/', '-', '\\'],
    'OSX': ["⠄", "⠆", "⠇", "⠋", "⠙", "⠸", "⠰", "⠠", "⠰", "⠸", "⠙", "⠋", "⠇", "⠆"]
}

ICON_ERROR = {
    'WINDOWS': 'X',
    'OSX': '✗'
}

ICON_SUCCESS = {
    'WINDOWS': '√',
    'OSX': '✓'
}
