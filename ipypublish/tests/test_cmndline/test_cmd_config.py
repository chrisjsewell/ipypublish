import pytest
from click.testing import CliRunner
from ipypublish.cmdline.commands.cmd_config import (list_default_traits, list_export_configs)
from ipypublish.cmdline.commands.cmd_ipypub import (autocomplete, AUTOCOMPLETE_COMMAND)


def test_autocomplete():

    runner = CliRunner()
    result = runner.invoke(autocomplete)
    assert result.exception is None, result.output
    assert result.exit_code == 0, result.output
    assert result.output.strip() == AUTOCOMPLETE_COMMAND, result.output


def test_default_traits():

    runner = CliRunner()
    result = runner.invoke(list_default_traits)
    assert result.exception is None, result.output
    assert result.exit_code == 0, result.output
    assert result.output, result.output


@pytest.mark.parametrize('options', ((), ('-v',), ('--verbosity',), ('-r', ''), ('--filter-regex', 'sphinx')))
def test_list_configs(options):

    runner = CliRunner()
    result = runner.invoke(list_export_configs, options)
    assert result.exception is None, result.output
    assert result.exit_code == 0, result.output
    assert result.output, result.output
