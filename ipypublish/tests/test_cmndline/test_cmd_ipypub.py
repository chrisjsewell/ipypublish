import pytest
from click.testing import CliRunner
from ipypublish.cmdline.commands.cmd_ipypub import (ipub_default_traits, ipub_list_configs, autocomplete,
                                                    AUTOCOMPLETE_COMMAND)


def test_autocomplete():

    runner = CliRunner()
    result = runner.invoke(autocomplete)
    assert result.exception is None, result.output
    assert result.output.strip() == AUTOCOMPLETE_COMMAND, result.output


def test_default_traits():

    runner = CliRunner()
    result = runner.invoke(ipub_default_traits)
    assert result.exception is None, result.output
    assert result.output, result.output


@pytest.mark.parametrize('options', ((), ('-v',), ('--verbose',), ('-r', ''), ('--filter-regex', 'sphinx')))
def test_list_configs(options):

    runner = CliRunner()
    result = runner.invoke(ipub_list_configs, options)
    assert result.exception is None, result.output
    assert result.output, result.output
