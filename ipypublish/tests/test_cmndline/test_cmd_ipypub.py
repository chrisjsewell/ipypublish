import pytest
from click.testing import CliRunner
from ipypublish.cmdline.commands.cmd_ipypub import ipypub
from ipypublish.cmdline.options import _AUTOCOMPLETE_COMMAND


@pytest.mark.parametrize('options', (('-a',), ('--autocomplete',)))
def test_autocomplete(options):

    runner = CliRunner()
    result = runner.invoke(ipypub, options)
    assert result.exception is None, result.output
    assert result.exit_code == 0, result.output
    assert result.output.strip() == _AUTOCOMPLETE_COMMAND, result.output
