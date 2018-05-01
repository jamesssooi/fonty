'''fonty.lib.config'''
import os
import configparser

from fonty.lib.constants import APP_DIR, CONFIG_FILENAME


class CommonConfiguration(dict):
    '''The CommonConfiguration contains fonty's global configuration values.'''

    #: Enables telemetry
    telemetry: bool = True


def load_config(path: str = os.path.join(APP_DIR, CONFIG_FILENAME)):
    '''Load configuration values from the configuration file.'''

    # Parse configuration files
    config = configparser.ConfigParser()
    config.read(path)

    # Read `common` configuration values
    if 'common' in config:
        CommonConfiguration.telemetry = config.getboolean('common', 'telemetry')
