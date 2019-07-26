""" utility functions for ``click`` cli """
import logging

import click


class ColorFormatter(logging.Formatter):
    """ class to format logging message levels with ``click`` colors"""
    colors = {
        'error': dict(fg='red'),
        'exception': dict(fg='red'),
        'critical': dict(fg='red'),
        # 'debug': dict(fg='blue'),
        'info': dict(fg='blue'),
        'warning': dict(fg='yellow')
    }

    def format(self, record):
        if not record.exc_info:
            level = record.levelname.lower()
            if level in self.colors:
                record.levelname = click.style(level.upper(), **self.colors[level])

        return super(ColorFormatter, self).format(record)
