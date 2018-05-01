'''fonty.lib.telemetry'''
import sys
import platform
import threading
from enum import Enum
from datetime import datetime
from typing import Tuple

import distro
import requests
from fonty.version import __version__
from fonty.lib.constants import TELEMETRY_ENDPOINT
from fonty.lib.config import CommonConfiguration


class TelemetryEventTypes(Enum):
    '''An enum of possible telemetry event types.'''
    INSTALL_FONTS = 'INSTALL_FONTS'
    FONT_SEARCH_NO_RESULTS = 'FONT_SEARCH_NO_RESULTS'
    UNINSTALL_FONTS = 'UNINSTALL_FONTS'
    CONVERT_FONTS = 'CONVERT_FONTS'
    ADD_SOURCE = 'ADD_SOURCE'
    REMOVE_SOURCE = 'REMOVE_SOURCE'
    UPDATE_SOURCE = 'UPDATE_SOURCE'


class TelemetryEvent:
    '''The TelemetryEvent class describes a fonty telemetry event.

    By default, fonty sends some light usage data to better understand (1) how
    users use fonty and (2) also to identify interesting font usage statistics.
    It can however be disabled by turning off the `telemetry` setting in the
    fonty configuration file.
    '''

    #: The event type of this telemetry event.
    event_type: TelemetryEventTypes

    #: The timestamp of this telemetry event.
    timestamp: datetime

    #: The fonty version currently being used.
    fonty_version: str

    #: The operating system family of the current environment.
    os_family: str

    #: The operating system version of the current environment.
    os_version: str

    #: The current Python version.
    python_version: str

    #: The additional data that is relevant to this telemetry event.
    data: dict

    def __init__(
        self,
        event_type: TelemetryEventTypes,
        data: dict = None
    ) -> None:
        self.event_type = event_type
        self.timestamp = datetime.now()
        self.fonty_version = __version__
        self.python_version = '{major}.{minor}.{micro}'.format(
            major=sys.version_info.major,
            minor=sys.version_info.minor,
            micro=sys.version_info.micro
        )
        self.os_family, self.os_version = TelemetryEvent._get_os_info()
        self.data = data

    def send(self, force=False, asynchronous=True) -> None:
        '''Sends the telemetry data to the central logging server.'''
        if not CommonConfiguration.telemetry and not force:
            return

        # Create payload
        d = {
            'event_type': self.event_type.value,
            'timestamp': self.timestamp,
            'fonty_version': self.fonty_version,
            'os_family': self.os_family,
            'os_version': self.os_version,
            'python_version': self.python_version,
            'data': self.data
        }

        # Send request
        if asynchronous:
            threading.Thread(target=self._send_request, args=(d,)).start()
        else:
            self._send_request(d)

    def _send_request(self, d):
        try:
            requests.post(TELEMETRY_ENDPOINT, data=d)
        except:
            pass

    @staticmethod
    def _get_os_info() -> Tuple[str, str]:
        '''Gets the current operating system information and returns it as a
           tuple of (family, version).
        '''
        family = platform.system()
        version = ''

        if family.lower() == 'darwin':
            version = platform.mac_ver()[0]
        elif family.lower() == 'windows':
            win = sys.getwindowsversion()
            version = '{}.{}-{}-{}'.format(win.major, win.minor, win.build, win.platform)
        elif family.lower() == 'linux':
            dist = distro.linux_distribution(full_distribution_name=False)
            version = '{}-{}'.format(dist[0], dist[1])
        else:
            version = platform.platform()

        return family, version
