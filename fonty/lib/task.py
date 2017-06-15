'''task.py'''

import sys
import time
import threading
from termcolor import colored
from enum import Enum

TaskStatus = Enum('TaskStatus', 'SUCCESS ERROR WAITING')

class Task(object):
    STATUS_SUCCESS = '✓'
    STATUS_ERROR = '✗'
    STATUS_WAITING = ["⠄", "⠆", "⠇", "⠋", "⠙", "⠸", "⠰", "⠠", "⠰", "⠸", "⠙", "⠋", "⠇", "⠆"]
    DELAY = 0.2

    status = TaskStatus.WAITING
    active = True
    current_message = ''
    nl = True

    _indicator_iteration = 0
    _done = False

    def __init__(self, message, nl=True):
        self.message = message
        self.nl = nl
        threading.Thread(target=self.loop, daemon=True).start()

    def loop(self):
        '''Main print loop.'''

        while True:
            # clear previous line
            sys.stdout.write('\r{}\r'.format(' ' * len(self.current_message)))
            sys.stdout.flush()

            # generate new message
            self.current_message = '{indicator} {message}'.format(
                indicator=self.get_indicator(),
                message=self.message
            )

            # write new line
            sys.stdout.write(self.current_message)
            sys.stdout.flush()

            # exit condition
            if not self.active:
                if self.nl:
                    sys.stdout.write('\n')
                    sys.stdout.flush()
                self._done = True
                break

            time.sleep(self.DELAY)
    
    def stop(self, status=None, message=None):
        '''Stops this task.'''

        self.active = False
        if status: self.status = status
        if message: self.message = message

        # Wait until last loop iteration is complete before advancing.
        # This prevents a race condition where the print loop overwrites
        # any subsequent print statements.
        while not self._done:
            pass
    
    def get_indicator(self):
        '''Returns the current active indicator.'''

        indicator = ''
        if self.status == TaskStatus.WAITING:
            indicator = colored(self.STATUS_WAITING[self._indicator_iteration], 'blue')
            self._indicator_iteration += 1
            if (self._indicator_iteration >= len(self.STATUS_WAITING)):
                self._indicator_iteration = 0
        elif self.status == TaskStatus.ERROR:
            indicator = colored(self.STATUS_ERROR, 'red')
        elif self.status == TaskStatus.SUCCESS:
            indicator = colored(self.STATUS_SUCCESS, 'green')
        
        return indicator
