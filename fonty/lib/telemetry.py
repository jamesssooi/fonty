'''fonty.lib.telemetry'''
import sys
import platform
from enum import Enum
from datetime import datetime
from typing import Tuple

import distro
from fonty.version import __version__


class TelemetryEventTypes(Enum):
    '''An enum of possible telemetry event types.'''
    INSTALL_FONTS = 'INSTALL_FONTS'
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
        self.os_family, self.os_version = TelemetryEvent._get_os_info()
        self.data = data

    def send(self, force=False) -> None:
        '''Sends the telemetry data to the central logging server.'''
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
