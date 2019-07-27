import os
import pytest
from click.testing import CliRunner
from ipypublish.cmdline.commands import cmd_config
from ipypublish.cmdline.config import IpubClickConfig, CONFIG_FILENAME


@pytest.mark.parametrize('options', (('-f',), ('--file-path',)))
def test_config_filepath(options):

    runner = CliRunner()
    result = runner.invoke(cmd_config.config, options, obj=IpubClickConfig())
    assert result.exception is None, result.output
    assert result.exit_code == 0, result.output
    assert CONFIG_FILENAME in result.output, result.output


def test_show(temp_folder):

    config = IpubClickConfig(temp_folder)
    config._save_data({'a': 'test'})
    runner = CliRunner()
    result = runner.invoke(cmd_config.show, obj=config)
    assert result.exception is None, result.output
    assert result.exit_code == 0, result.output
    assert 'test' in result.output, result.output


def test_reset(temp_folder):

    config = IpubClickConfig(temp_folder)
    config._save_data({'a': 'test'})
    runner = CliRunner()
    result = runner.invoke(cmd_config.reset, obj=config, input='y')
    assert result.exception is None, result.output
    assert result.exit_code == 0, result.output
    assert config.dict == {}


@pytest.mark.parametrize('argument', ('', 'does/not/exist'))
def test_add_export_path_exception(temp_folder, argument):

    config = IpubClickConfig(temp_folder)
    runner = CliRunner()
    result = runner.invoke(cmd_config.add_export_path, [argument], obj=config)
    assert result.exception is not None, result.output


def test_add_export_path(temp_folder):

    config = IpubClickConfig(temp_folder)
    runner = CliRunner()
    result = runner.invoke(cmd_config.add_export_path, [temp_folder], obj=config)
    assert result.exception is None, result.output
    assert result.exit_code == 0, result.output
    assert config.dict == {'export_paths': [os.path.normpath(os.path.realpath(temp_folder))]}


@pytest.mark.parametrize('options', ((), ('-v',), ('--verbosity',), ('-r', ''), ('--filter-regex', 'sphinx')))
def test_list_export_configs(options):

    runner = CliRunner()
    result = runner.invoke(cmd_config.list_export_configs, options)
    assert result.exception is None, result.output
    assert result.exit_code == 0, result.output
    assert result.output, result.output


def test_list_default_traits():

    runner = CliRunner()
    result = runner.invoke(cmd_config.list_default_traits)
    assert result.exception is None, result.output
    assert result.exit_code == 0, result.output
    assert result.output, result.output
