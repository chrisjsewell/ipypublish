import os
import traceback

import pytest
from click.testing import CliRunner

from ipypublish.cmdline.commands.cmd_publish import ipub_publish
from ipypublish.cmdline.config import IpubClickConfig


@pytest.mark.ipynb('basic_nb')
def test_non_existent_config(ipynb_app):

    options = [
        str(ipynb_app.input_file), '-f', 'non-existent', '--outpath',
        str(ipynb_app.converted_path), '--dry-run', '--log-level', 'debug'
    ]
    runner = CliRunner()
    result = runner.invoke(ipub_publish, options)
    assert result.exception is not None, result.output


@pytest.mark.ipynb('basic_nb')
def test_bad_config(ipynb_app):
    options = [
        str(ipynb_app.input_file), '-f', 'bad.json', '--outpath',
        str(ipynb_app.converted_path), '--dry-run', '--log-level', 'debug'
    ]
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('bad.json', 'w') as f:
            f.write('{"a": 1}')
        result = runner.invoke(ipub_publish, options)
        assert result.exception is not None, result.output
        # assert "jsonschema.exceptions.ValidationError" in result.output


@pytest.mark.ipynb('basic_nb')
def test_nbpublish_dry_run_std(ipynb_app):

    options = [
        str(ipynb_app.input_file), '--outpath',
        str(ipynb_app.converted_path), '--dry-run', '--log-level', 'debug', '-pt'
    ]
    runner = CliRunner()
    result = runner.invoke(ipub_publish, options)
    assert result.exception is None, traceback.print_tb(result.exc_info[2])
    assert 'SUCCESS' in result.output


@pytest.mark.ipynb('basic_nb')
def test_nbpublish_dry_run_with_external_plugin_path(ipynb_app, external_export_plugin):

    options = [
        str(ipynb_app.input_file), '--outformat',
        str(external_export_plugin), '--outpath',
        str(ipynb_app.converted_path), '--dry-run', '--log-level', 'debug', '-pt'
    ]
    runner = CliRunner()
    result = runner.invoke(ipub_publish, options)
    assert result.exception is None, result.output
    assert 'SUCCESS' in result.output


@pytest.mark.ipynb('basic_nb')
def test_nbpublish_dry_run_with_external_plugin_key(ipynb_app, external_export_plugin, temp_folder):

    options = [
        str(ipynb_app.input_file), '--outformat',
        os.path.splitext(str(external_export_plugin.name))[0], '--outpath',
        str(ipynb_app.converted_path), '--dry-run', '--log-level', 'debug', '-pt'
    ]
    config = IpubClickConfig(temp_folder)
    config.add_export_path(str(external_export_plugin.parent))
    runner = CliRunner()
    result = runner.invoke(ipub_publish, options, obj=config)
    assert result.exception is None, result.output
    assert 'SUCCESS' in result.output


@pytest.mark.ipynb('basic_nb')
def test_nbpublish_write(ipynb_app):

    options = [
        str(ipynb_app.input_file), '--outformat', 'latex_ipypublish_main', '--outpath',
        str(ipynb_app.converted_path), '-pt'
    ]
    runner = CliRunner()
    result = runner.invoke(ipub_publish, options)
    assert result.exception is None, result.output
    assert 'SUCCESS' in result.output
    assert ipynb_app.converted_path.joinpath(ipynb_app.input_file.name.replace('.ipynb', '.tex')).exists()


@pytest.mark.requires_latexmk
@pytest.mark.ipynb('basic_nb')
def test_nbpublish_to_pdf(ipynb_app):

    options = [
        str(ipynb_app.input_file), '--outformat', 'latex_ipypublish_main', '--outpath',
        str(ipynb_app.converted_path), '--create-pdf', '-pt'
    ]
    runner = CliRunner()
    result = runner.invoke(ipub_publish, options)
    assert result.exception is None, result.output
    assert 'SUCCESS' in result.output
    assert ipynb_app.converted_path.joinpath(ipynb_app.input_file.name.replace('.ipynb', '.pdf')).exists()
