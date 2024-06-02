import os

import pytest

ROOT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


@pytest.fixture()
def gtfs_nyc() -> str:
    return os.path.join(ROOT_FOLDER, 'tests', 'data', 'gtfs_nyc.zip')
