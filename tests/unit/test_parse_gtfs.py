import dataclasses
import io

import pandas as pd
import pytest

from gtfs_filtering.core import parse_gtfs, OPTIONAL_GTFS_FILES


@pytest.fixture()
def parse_gtfs_file_return_value() -> pd.DataFrame:
    gtfs_file_content = """agency_id,agency_name,agency_url,agency_timezone,agency_lang,agency_phone
MTA NYCT,MTA New York City Transit,http://www.mta.info,America/New_York,en,718-330-1234"""
    return pd.read_csv(io.StringIO(gtfs_file_content), dtype=str)


@pytest.fixture()
def mock_parse_gtfs_file_all_files_present(parse_gtfs_file_return_value: pd.DataFrame, monkeypatch: pytest.MonkeyPatch):
    def mock_parse_gtfs_file(_directory, _filename) -> pd.DataFrame:
        return parse_gtfs_file_return_value

    monkeypatch.setattr('gtfs_filtering.core.parse_gtfs_file', mock_parse_gtfs_file)


def build_mock_parse_gtfs_file_missing(parse_gtfs_file_return_value: pd.DataFrame, missing_filename: str):
    def mock_parse_gtfs_file(directory: str, filename: str) -> pd.DataFrame:
        if filename == missing_filename:
            e = FileNotFoundError()
            e.filename = missing_filename
            raise e
        return parse_gtfs_file_return_value

    return mock_parse_gtfs_file


def test_parse_gtfs__when_all_files_present__returns_gtfs_object(mock_parse_gtfs_file_all_files_present):
    gtfs = parse_gtfs('gtfs')

    for field in dataclasses.fields(gtfs):
        assert gtfs.__getattribute__(field.name) is not None, f'field {field.name} should not be None'
        assert isinstance(gtfs.__getattribute__(field.name), pd.DataFrame), f'field {field.name} should be a DataFrame'


@pytest.mark.parametrize('missing_filename', [
    'agency.txt',
    'stops.txt',
    'routes.txt',
    'trips.txt'
])
def test_parse_gtfs__when_missing_required_file__raises_file_not_found_error(missing_filename: str,
                                                                             parse_gtfs_file_return_value: pd.DataFrame,
                                                                             monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr('gtfs_filtering.core.parse_gtfs_file',
                        build_mock_parse_gtfs_file_missing(parse_gtfs_file_return_value, missing_filename))

    with pytest.raises(FileNotFoundError):
        parse_gtfs('gtfs')


@pytest.mark.parametrize('missing_filename', OPTIONAL_GTFS_FILES)
def test_parse_gtfs__when_missing_optional_file__returns_gtfs_object(missing_filename: str,
                                                                     parse_gtfs_file_return_value: pd.DataFrame,
                                                                     monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr('gtfs_filtering.core.parse_gtfs_file',
                        build_mock_parse_gtfs_file_missing(parse_gtfs_file_return_value, missing_filename))

    gtfs = parse_gtfs('gtfs')

    for field in dataclasses.fields(gtfs):
        if field.name == missing_filename.rstrip('.txt'):
            # missing file is None
            assert gtfs.__getattribute__(field.name) is None, f'field {field.name} should be None'
        else:
            assert gtfs.__getattribute__(field.name) is not None, f'field {field.name} should not be None'
            assert isinstance(gtfs.__getattribute__(field.name),
                              pd.DataFrame), f'field {field.name} should be a DataFrame'
