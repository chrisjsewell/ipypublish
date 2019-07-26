import pytest
from click.testing import CliRunner

from ipypublish.cmdline.commands.cmd_present import ipub_present


@pytest.mark.ipynb('basic_nb')
def test_bad_exporter(ipynb_app):

    options = [
        str(ipynb_app.input_file), '-f', 'non-existent', '--outpath',
        str(ipynb_app.converted_path), '--dry-run', '--log-level', 'debug'
    ]
    runner = CliRunner()
    result = runner.invoke(ipub_present, options)
    assert result.exception is not None, result.output


@pytest.mark.ipynb('basic_nb')
def test_nbpresent_dry_run(ipynb_app):

    options = [
        str(ipynb_app.input_file), '--outpath',
        str(ipynb_app.converted_path), '--dry-run', '--log-level', 'debug', '-pt'
    ]
    runner = CliRunner()
    result = runner.invoke(ipub_present, options)
    assert result.exception is None, result.output
    assert 'SUCCESS' in result.output
