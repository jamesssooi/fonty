'''fonty.lib.task.py: Module to print task statements on console.'''
import sys
import time
import threading
from enum import Enum
from typing import Union, List, cast

from ansiwrap import shorten, ansilen
from termcolor import colored
from fonty.lib.terminal_size import get_terminal_size
from fonty.lib.constants import IS_WINDOWS, ICON_WAITING, ICON_SUCCESS, ICON_ERROR


class TaskStatus(Enum):
    '''Represents a task status.'''
    SUCCESS = 1
    ERROR = 2
    WAITING = 3
    WARNING = 4


class Task(object):
    '''`Task` is an utility class that prints a pretty, elegant, and animating
    task string to the console.

    It functions by spawning a daemon thread that executes an infinite loop
    block that prints (and rewrites) a message until `Task.stop()` is called.
    Because `Task` relies on printing and rewriting the same line over and over
    again, it is important not to use any print statements until `Task.stop()`
    is called. Example output:

        WAITING: `⠙ Loading unicorns...`

        SUCCESS: `✓ Loaded unicorns!`

        ERROR: `✗ Unicorns do not exist`
    '''

    #: The `waiting` status icon.
    STATUS_WAITING: Union[str, List[str]] = ICON_WAITING['WINDOWS'] \
        if IS_WINDOWS else ICON_WAITING['OSX']

    #: The `error` status icon.
    STATUS_ERROR: Union[str, List[str]] = ICON_ERROR['WINDOWS'] \
        if IS_WINDOWS else ICON_ERROR['OSX']
    
    #: The `success` status icon.
    STATUS_SUCCESS: Union[str, List[str]] = ICON_SUCCESS['WINDOWS'] \
        if IS_WINDOWS else ICON_SUCCESS['OSX']

    #: The `warning` status icon.
    STATUS_WARNING: Union[str, List[str]] = '!'

    #: The animation delay per frame.
    DELAY: float = 0.2

    #: The current message of the task.
    message: str

    #: The current status of the task.
    status: TaskStatus = TaskStatus.WAITING

    #: Indicates whether the task is active or not.
    active: bool = True

    #: Indicates whether the task message should be truncated or not.
    truncate: bool = True

    #: The annotated and full message of the task.
    _current_message: str = ''

    #: The current frame of the active indicator.
    _indicator_iteration: int = 0

    #: Indicates whether the print loop is done.
    _done: bool = False

    def __init__(
        self,
        message: str,
        status: TaskStatus = TaskStatus.WAITING,
        asynchronous: bool = True,
        truncate: bool = True
    ) -> None:
        self.message = message
        self.status = status
        self.truncate = truncate

        if asynchronous:
            threading.Thread(target=self.loop, daemon=True).start()
        else:
            self.active = False
            self.loop() # Prints only one iteration

    def loop(self) -> None:
        '''Main print loop.'''

        while True:
            # Clear previous line
            sys.stdout.write('\r{}\r'.format(' ' * ansilen(self._current_message)))
            sys.stdout.flush()

            # Generate new message
            self._current_message = '{indicator} {message}'.format(
                indicator=self.get_indicator(),
                message=self.message,
            )

            # Truncate the output if it is longer than terminal width
            # This is necessary because if the output is wrapped, there would
            # be problems with the output not clearing all lines.
            if self.truncate:
                term_width, _ = get_terminal_size()
                self._current_message = shorten(text=self._current_message,
                                               width=term_width,
                                               placeholder='...')

            # Write new line
            sys.stdout.write(self._current_message)
            sys.stdout.flush()

            # Exit condition
            if not self.active:
                sys.stdout.write('\n')
                sys.stdout.flush()
                self._done = True
                break

            time.sleep(self.DELAY)

    def stop(self, message: str = None, status: TaskStatus = TaskStatus.SUCCESS) -> None:
        '''Stop this task.'''

        self.active = False
        self.truncate = False
        if status:
            self.status = status
        if message:
            self.message = message

        # Wait until last loop iteration is complete before advancing.
        # This prevents a race condition where the print loop overwrites
        # any subsequent print statements.
        while not self._done:
            pass

    def complete(self, message: str = None) -> None:
        '''Stop this task with a success status.'''
        self.stop(message=message, status=TaskStatus.SUCCESS)

    def error(self, message: str = None) -> None:
        '''Stop this task with an error status.'''
        self.stop(status=TaskStatus.ERROR, message=message)

    def get_indicator(self) -> str:
        '''Returns the current active indicator.'''
        indicator = ''
        if self.status == TaskStatus.WAITING:
            indicator = colored(self.STATUS_WAITING[self._indicator_iteration], 'blue')
            self._indicator_iteration += 1
            if self._indicator_iteration >= len(self.STATUS_WAITING):
                self._indicator_iteration = 0
        elif self.status == TaskStatus.ERROR:
            indicator = colored(cast(str, self.STATUS_ERROR), 'red')
        elif self.status == TaskStatus.SUCCESS:
            indicator = colored(cast(str, self.STATUS_SUCCESS), 'green')
        elif self.status == TaskStatus.WARNING:
            indicator = colored(cast(str, self.STATUS_WARNING), 'yellow')

        return indicator
