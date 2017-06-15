# -*- coding: utf-8 -*-
'''progress.py'''

import math
from fonty.lib import utils

class ProgressBar(object):
    DEFAULT_FORMAT = '{desc}{bar} {percentage}'
    value = 0

    def __init__(self, total, desc=None, cols=15,
                 bar_format=DEFAULT_FORMAT,
                 filled_char='█', empty_char='░'):
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