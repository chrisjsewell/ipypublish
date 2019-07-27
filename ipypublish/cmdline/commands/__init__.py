"""The `ipub` command line interface."""
from __future__ import absolute_import
import click_completion

# TODO this patch can be removed once this PR is merged https://github.com/click-contrib/click-completion/pull/27/
from ipypublish.cmdline.patch import get_choices
click_completion.core.get_choices = get_choices

# Activate the completion of parameter types provided by the click_completion package
click_completion.init()

# Import to populate the `ipypub` sub commands
from .cmd_config import *  # noqa: F401,F403
from .cmd_publish import *  # noqa: F401,F403
from .cmd_present import *  # noqa: F401,F403
