from os.path import abspath, join, dirname
from typing import List
from zipfile import ZipFile

import pytest

ROOT_FOLDER = abspath(join(dirname(__file__), '..', '..'))


@pytest.fixture()
def gtfs_nyc() -> str:
    return join(ROOT_FOLDER, 'tests', 'data', 'gtfs_nyc.zip')


@pytest.fixture()
def existing_output_gtfs(tmp_path) -> str:
    filepath = join(tmp_path, 'output_gtfs.zip')
    with open(filepath, 'w') as f:
        f.write('')     # empty zip file, just to test existence
    return filepath


@pytest.fixture()
def output_gtfs(tmp_path) -> str:
    return join(tmp_path, 'output_gtfs.zip')


@pytest.fixture()
def route_ids() -> List[str]:
    return ['1', '2', '3']


@pytest.fixture()
def route_ids() -> List[str]:
    return ['AFA23GEN-1038-Sunday-00_000600_1..S03R', 'AFA23GEN-1038-Sunday-00_009200_1..N03R']
