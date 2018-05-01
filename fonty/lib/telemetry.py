'''fonty.lib.telemetry'''
import sys
import json
import platform
import threading
from enum import Enum
from datetime import datetime
from typing import Tuple

import requests
from fonty.version import __version__
from fonty.lib.json_encoder import FontyJSONEncoder
from fonty.lib.constants import TELEMETRY_ENDPOINT, JSON_DUMP_OPTS
from fonty.lib.config import CommonConfiguration


class TelemetryEventTypes(Enum):
    '''An enum of possible telemetry event types.'''
    FONTY_SETUP = 'FONTY_SETUP'
    FONT_INSTALL = 'FONT_INSTALL'
    FONT_UNINSTALL = 'FONT_UNINSTALL'
    FONT_LIST = 'FONT_LIST'
    FONT_LIST_REBUILD = 'FONT_LIST_REBUILD'
    FONT_CONVERT = 'FONT_CONVERT'
    SOURCE_LIST = 'SOURCE_LIST'
    SOURCE_ADD = 'SOURCE_ADD'
    SOURCE_REMOVE = 'SOURCE_REMOVE'
    SOURCE_UPDATE = 'SOURCE_UPDATE'


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

    #: The time it took (in seconds) to execute this event.
    execution_time: float

    #: The status code of the current command. 0 means success, >1 means error.
    status_code: int

    #: The additional data that is relevant to this telemetry event.
    data: dict

    def __init__(
        self,
        status_code: int,
        event_type: TelemetryEventTypes,
        execution_time: float = None,
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
        self.execution_time = execution_time
        self.status_code = status_code
        self.data = data

    def send(self, force=False, asynchronous=True) -> None:
        '''Sends the telemetry data to the central logging server.'''
        if not CommonConfiguration.telemetry and not force:
            return

        # Create payload
        d = {
            'timestamp': self.timestamp,
            'status_code': self.status_code,
            'event_type': self.event_type.value,
            'execution_time': self.execution_time,
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
            requests.post(
                url=TELEMETRY_ENDPOINT,
                data=json.dumps(d, cls=FontyJSONEncoder, **JSON_DUMP_OPTS),
                headers={'Content-Type': 'application/json'}
            )
        except: # pylint: disable=W0702
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
            win = sys.getwindowsversion() # pylint: disable=E1101
            version = '{}.{}-{}-{}'.format(win.major, win.minor, win.build, win.platform)
        elif family.lower() == 'linux':
            import distro
            dist = distro.linux_distribution(full_distribution_name=False)
            version = '{}-{}'.format(dist[0], dist[1])
        else:
            version = platform.platform()

        return family, version
