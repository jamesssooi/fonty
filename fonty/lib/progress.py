# -*- coding: utf-8 -*-
'''progress.py'''

import sys
import time
import threading
import math
import colorama
from termcolor import colored
from fonty.lib import utils

colorama.init()

class ProgressBar(object):
    DEFAULT_FORMAT = '{desc}{bar}{percentage}'
    value = 0

    def __init__(self, total, desc=None, cols=15,
                 bar_format='{desc}{bar} {percentage}',
                 filled_char='█', empty_char=' '):
        self.total = total
        self.desc = desc
        self.cols = cols
        self.filled_char = filled_char
        self.empty_char = empty_char
        self.bar_format = bar_format
    
    def __str__(self):
        percentage = self.value / self.total

        # Draw bar
        fill_count = math.ceil(min(percentage, 1) * self.cols)
        empty_count = self.cols - fill_count
        bar = '|{fill}{empty}|'.format(
            fill=self.filled_char * int(fill_count),
            empty=self.empty_char * int(empty_count)
        )

        # Format output
        s = self.bar_format.format(
            desc=utils.xstr(self.desc),
            bar=bar,
            percentage=str(round(percentage * 100)) + '%'
        )

        return s

    def increment(self, n=1):
        self.value += n
    
    def update(self, n):
        self.value = n


class Action:
    #ANIMATION = ['[-  ]', '[ - ]', '[  -]', '[ - ]']
    #ANIMATION = ['[⠄ ]', '[⠠ ]', '[ ⠄]', '[ ⠠]', '[ ⠄]', '[⠠ ]']
    ANIMATION = ["⠄", "⠆", "⠇", "⠋", "⠙", "⠸", "⠰", "⠠", "⠰", "⠸", "⠙", "⠋", "⠇", "⠆"]
    DELAY = 0.2

    iteration = 0
    current_message = ''

    def __init__(self, message, active=True):
        self.message = message
        self.active = active
        threading.Thread(target=self.loop).start()
    
    def loop(self):
        while self.active:
            sys.stdout.write('\r')
            sys.stdout.flush()
            self.current_message = '{animation} {message}'.format(
                animation=colored(self.ANIMATION[self.iteration], 'blue'),
                message=self.message
            )
            sys.stdout.write(self.current_message)
            sys.stdout.flush()

            self.iteration += 1
            if self.iteration >= len(self.ANIMATION):
                self.iteration = 0
            
            time.sleep(self.DELAY)
    
    def stop(self, status=None, message=None):
        self.active = False
        
        if not message:
            message = self.message

        if status:
            s = '{status} {message}'.format(status=status, message=message)
        else:
            s = message
        
        # TODO: Move this into main draw loop to prevent race conditions
        # Clear line
        sys.stdout.write('\r{}\r'.format(' ' * len(self.current_message)))
        sys.stdout.flush()

        # Write line
        sys.stdout.write(s)
        sys.stdout.flush()
        
        # Move down one line
        sys.stdout.write('\n')
        sys.stdout.flush()
