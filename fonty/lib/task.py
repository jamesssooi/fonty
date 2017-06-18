'''fonty.lib.task.py: Module to print task statements on console.'''
import sys
import time
import threading
from enum import Enum

from ansiwrap import shorten, ansilen
from termcolor import colored
from fonty.lib.terminal_size import get_terminal_size

TaskStatus = Enum('TaskStatus', 'SUCCESS ERROR WAITING')

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
    STATUS_SUCCESS = '✓'
    STATUS_ERROR = '✗'
    STATUS_WAITING = ["⠄", "⠆", "⠇", "⠋", "⠙", "⠸", "⠰", "⠠", "⠰", "⠸", "⠙", "⠋", "⠇", "⠆"]
    DELAY = 0.2

    status = TaskStatus.WAITING
    active = True
    current_message = ''

    _indicator_iteration = 0
    _done = False

    def __init__(self, message: str, short_message: str = None) -> None:
        self.message = message
        self.short_message = short_message if short_message else message
        threading.Thread(target=self.loop, daemon=True).start()

    def loop(self) -> None:
        '''Main print loop.'''

        while True:
            # Clear previous line
            sys.stdout.write('\r{}\r'.format(' ' * ansilen(self.current_message)))
            sys.stdout.flush()

            # Generate new message
            self.current_message = '{indicator} {message}'.format(
                indicator=self.get_indicator(),
                message=self.message,
            )

            # Truncate the output if it is longer than terminal width
            # This is necessary because if the output is wrapped, there would
            # be problems with the output not clearing all lines.
            term_width, _ = get_terminal_size()
            self.current_message = shorten(text=self.current_message,
                                           width=term_width,
                                           placeholder='...')

            # Write new line
            sys.stdout.write(self.current_message)
            sys.stdout.flush()

            # Exit condition
            if not self.active:
                sys.stdout.write('\n')
                sys.stdout.flush()
                self._done = True
                break

            time.sleep(self.DELAY)

    def stop(self,
             status: TaskStatus = TaskStatus.SUCCESS,
             message: str = None) -> None:
        '''Stop this task.'''

        self.active = False
        if status:
            self.status = status
        if message:
            self.message = message

        # Wait until last loop iteration is complete before advancing.
        # This prevents a race condition where the print loop overwrites
        # any subsequent print statements.
        while not self._done:
            pass

    def get_indicator(self) -> str:
        '''Returns the current active indicator.'''

        indicator = ''
        if self.status == TaskStatus.WAITING:
            indicator = colored(self.STATUS_WAITING[self._indicator_iteration], 'blue')
            self._indicator_iteration += 1
            if self._indicator_iteration >= len(self.STATUS_WAITING):
                self._indicator_iteration = 0
        elif self.status == TaskStatus.ERROR:
            indicator = colored(self.STATUS_ERROR, 'red')
        elif self.status == TaskStatus.SUCCESS:
            indicator = colored(self.STATUS_SUCCESS, 'green')

        return indicator
