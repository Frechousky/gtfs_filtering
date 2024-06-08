import os
import typing

import pytest

ROOT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


@pytest.fixture()
def gtfs_nyc() -> str:
    return os.path.join(ROOT_FOLDER, 'tests', 'data', 'gtfs_nyc.zip')


@pytest.fixture()
def existing_output_gtfs(tmp_path) -> str:
    filepath = os.path.join(tmp_path, 'output_gtfs.zip')
    with open(filepath, 'w') as f:
        f.write('')     # empty zip file, just to test existence
    return filepath


@pytest.fixture()
def output_gtfs(tmp_path) -> str:
    return os.path.join(tmp_path, 'output_gtfs.zip')


@pytest.fixture()
def route_ids() -> typing.List[str]:
    return ['1', '2', '3']


@pytest.fixture()
def route_ids() -> typing.List[str]:
    return ['AFA23GEN-1038-Sunday-00_000600_1..S03R', 'AFA23GEN-1038-Sunday-00_009200_1..N03R']
