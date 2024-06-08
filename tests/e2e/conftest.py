import os
import subprocess
import typing

import pytest

ROOT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


@pytest.fixture()
def gtfs_nyc() -> str:
    path = os.path.join(ROOT_FOLDER, 'tests', 'data', 'gtfs_nyc.zip')
    assert os.path.isfile(path), f'{path} should exist'
    return path


@pytest.fixture()
def gtfs_missing_routes_txt() -> str:
    path = os.path.join(ROOT_FOLDER, 'tests', 'data', 'gtfs_missing_routes_txt.zip')
    assert os.path.isfile(path), f'{path} should exist'
    return path


@pytest.fixture()
def gtfs_empty_routes_txt() -> str:
    path = os.path.join(ROOT_FOLDER, 'tests', 'data', 'gtfs_empty_routes_txt.zip')
    assert os.path.isfile(path), f'{path} should exist'
    return path


@pytest.fixture()
def existing_output_gtfs(tmp_path) -> str:
    path = os.path.join(tmp_path, 'output_gtfs.zip')
    with open(path, 'w') as f:
        f.write('')  # empty zip file, just to test existence
    assert os.path.isfile(path), f'{path} should exist'
    return path


@pytest.fixture()
def output_gtfs(tmp_path) -> str:
    path = os.path.join(tmp_path, 'output_gtfs.zip')
    assert not os.path.isfile(path), f'{path} should not exist'
    return path


@pytest.fixture()
def route_ids() -> typing.List[str]:
    return ['1', '2', '3']


@pytest.fixture()
def trip_ids() -> typing.List[str]:
    return ['AFA23GEN-1038-Sunday-00_000600_1..S03R', 'AFA23GEN-1038-Sunday-00_009200_1..N03R']


@pytest.fixture()
def gtfs_validator_jar() -> str:
    path = os.path.join(ROOT_FOLDER, 'tests', 'bin', 'gtfs-validator-5.0.1-cli.jar')
    assert os.path.isfile(path), f'{path} should exist'
    return path


@pytest.fixture()
def validate_gtfs(gtfs_validator_jar, tmp_path) -> typing.Callable[[str], subprocess.CompletedProcess]:
    def inner(gtfs_zip_path: str) -> subprocess.CompletedProcess:
        return subprocess.run(["java", "-jar", gtfs_validator_jar, "-o", tmp_path, "-i", gtfs_zip_path])

    return inner
