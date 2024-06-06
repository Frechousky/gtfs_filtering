import os.path
from subprocess import run
from typing import List

import pytest

from tests.e2e.conftest import ROOT_FOLDER

CLI_PATH = os.path.join(ROOT_FOLDER, 'dist', 'cli')


@pytest.mark.parametrize('args',
                         [['--help'], ['--help', 'gtfs.zip', 'output.zip'], ['gtfs.zip', '--help', 'output.zip'],
                          ['gtfs.zip', 'output.zip', '--help'], ['--help', 'gtfs.zip', 'output.zip', '--help'], ])
def test_cli__when_help_option_is_present__displays_help(args: List[str]):
    output = run([CLI_PATH, *args], capture_output=True, text=True)

    assert output.returncode == 0, 'command should be successful'
    assert 'Usage: cli' in output.stdout, 'command should display help message to user'


def test_cli__when_input_gtfs_zip_arg_is_missing__fails_and_displays_error_message():
    output = run(CLI_PATH, capture_output=True, text=True)

    assert output.returncode == 2, 'command should fail'
    assert 'Usage: cli' in output.stderr, 'command should display help message to user'
    assert "Error: Missing argument 'INPUT_GTFS_ZIP'." in output.stderr, 'command should display error message to user'


def test_cli__when_input_gtfs_zip_does_not_exists__fails_and_displays_error_message():
    output = run([CLI_PATH, 'non_existing_file.zip'], capture_output=True, text=True)

    assert output.returncode == 2, 'command should fail'
    assert 'Usage: cli' in output.stderr, 'command should display help message to user'
    assert "Invalid value for 'INPUT_GTFS_ZIP': File 'non_existing_file.zip' does not exist." in output.stderr, 'command should display error message to user'


def test_cli__when_output_gtfs_zip_arg_is_missing__fails_and_displays_error_message(gtfs_nyc: str):
    output = run([CLI_PATH, gtfs_nyc], capture_output=True, text=True)

    assert output.returncode == 2, 'command should fail'
    assert 'Usage: cli' in output.stderr, 'command should display help message to user'
    assert "Error: Missing argument 'OUTPUT_GTFS_ZIP'." in output.stderr, 'command should display error message to user'


def test_cli__when_output_gtfs_zip_exists_and_overwrite_flag_not_set__fails_and_displays_error_message(gtfs_nyc: str,
                                                                                                       existing_output_gtfs: str,
                                                                                                       route_ids: List[
                                                                                                           str]):
    assert os.path.isfile(existing_output_gtfs), 'output_gtfs exists'

    output = run([CLI_PATH, gtfs_nyc, existing_output_gtfs, *route_ids], capture_output=True, text=True)

    assert output.returncode == 1, 'command should fail'
    assert f"Error: File '{existing_output_gtfs}' already exists." in output.stderr, 'command should display error message to user'


@pytest.mark.parametrize('overwrite_opt', ['-o', '--overwrite'])
def test_cli__when_output_gtfs_zip_exists_and_overwrite_flag_set__is_successful(gtfs_nyc: str, existing_output_gtfs: str,
                                                                                route_ids: List[str],
                                                                                overwrite_opt: str):
    assert os.path.isfile(existing_output_gtfs), 'output_gtfs exists'
    mtime_before = os.path.getmtime(existing_output_gtfs)

    output = run([CLI_PATH, overwrite_opt, gtfs_nyc, existing_output_gtfs, *route_ids], capture_output=True, text=True)

    assert output.returncode == 0, 'command is successful'
    assert os.path.getmtime(existing_output_gtfs) > mtime_before, 'output gtfs should be overwritten'
