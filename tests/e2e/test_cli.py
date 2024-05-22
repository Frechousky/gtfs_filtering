import os.path
import subprocess
import sys
import typing

import pytest

ROOT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CLI_PATH = os.path.join(ROOT_FOLDER, 'gtfs_filtering', 'cli.py')


@pytest.mark.parametrize('args', [
    ['--help'],
    ['--help', 'gtfs.zip', 'output.zip'],
    ['gtfs.zip', '--help', 'output.zip'],
    ['gtfs.zip', 'output.zip', '--help'],
    ['--help', 'gtfs.zip', 'output.zip', '--help'],
])
def test_cli__when_help_option_is_present__displays_help(args: typing.List[str]):

    output = subprocess.run([CLI_PATH, *args], capture_output=True, text=True)
    assert output.returncode == 0, 'return code should be 0'
    assert 'Usage: cli.py' in output.stdout, 'should print help message'
