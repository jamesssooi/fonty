# -*- coding: utf-8 -*-
'''progress.py'''

import math
from fonty.lib import utils

class ProgressBar(object):
    '''A simple, printable text-based progress bar.'''

    #: The format string of how to print the progress bar.
    DEFAULT_FORMAT: str = '{desc}|{bar}| {percentage}'

    # The current value of the progress bar.
    value = 0

    def __init__(
        self,
        total: int,
        desc: str = None,
        cols: int = 15,
        bar_format: str = DEFAULT_FORMAT,
        filled_char: str = '█',
        empty_char: str = '░'
    ) -> None:
        self.total = total
        self.desc = desc
        self.cols = cols
        self.filled_char = filled_char
        self.empty_char = empty_char
        self.bar_format = bar_format

    def __str__(self) -> str:
        percentage = self.value / self.total

        # Draw bar
        fill_count = math.ceil(min(percentage, 1) * self.cols)
        empty_count = self.cols - fill_count
        bar = '{fill}{empty}'.format(
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

    def increment(self, n: int = 1) -> None:
        '''Increments the value of the progress bar by n. Defaults to 1.'''
        self.value += n

    def update(self, n: int) -> None:
        '''Set the value of the progress bar.'''
        self.value = n
