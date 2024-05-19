import os

import pandas as pd
import pytest

from gtfs_filtering.core import parse_gtfs_file
from tests.unit.conftest import NOT_EXISTING_FILE, EMPTY_FILE, VALID_GTFS_FILE


def test_parse_gtfs_file__when_file_is_valid__returns_dataframe(tmp_path, valid_gtfs_file):
    res = parse_gtfs_file(tmp_path, VALID_GTFS_FILE)

    assert res is not None, 'should not be None'
    assert isinstance(res, pd.DataFrame), 'should be a DataFrame'


def test_parse_gtfs_file__when_directory_does_not_exist__raises_error():
    directory = '/invalid/directory/'
    assert not os.path.exists(directory), 'directory should not exist'

    with pytest.raises(FileNotFoundError):
        parse_gtfs_file(directory, VALID_GTFS_FILE)


def test_parse_gtfs_file__when_file_does_not_exist__raises_error(tmp_path, not_existing_file):
    assert not os.path.exists(os.path.join(tmp_path, NOT_EXISTING_FILE)), 'file should not exist'

    with pytest.raises(FileNotFoundError):
        parse_gtfs_file(tmp_path, NOT_EXISTING_FILE)


def test_parse_gtfs_file__when_file_is_empty__raises_error(tmp_path, empty_gtfs_file):
    with open(os.path.join(tmp_path, EMPTY_FILE), 'r') as f:
        assert f.read() == '', 'file should be empty'

    with pytest.raises(pd.errors.EmptyDataError):
        parse_gtfs_file(tmp_path, EMPTY_FILE)
