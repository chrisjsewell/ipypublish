"""The `ipub` command line interface."""
from __future__ import absolute_import
import click_completion

# Activate the completion of parameter types provided by the click_completion package
click_completion.init()

# Import to populate the `ipypub` sub commands
from .cmd_config import *  # noqa: F401,F403
from .cmd_publish import *  # noqa: F401,F403
from .cmd_present import *  # noqa: F401,F403
