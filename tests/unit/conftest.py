import os

import pytest

VALID_GTFS_FILE = 'agency.txt'
EMPTY_FILE = 'empty.txt'
NOT_EXISTING_FILE = 'not_existing.txt'

VALID_GTFS_FILE_CONTENT = """agency_id,agency_name,agency_url,agency_timezone,agency_lang,agency_phone
MTA NYCT,MTA New York City Transit,http://www.mta.info,America/New_York,en,718-330-1234"""


@pytest.fixture()
def valid_gtfs_file(tmp_path):
    """create valid GTFS file for testing, delete it after test"""
    filepath = os.path.join(tmp_path, VALID_GTFS_FILE)
    with open(filepath, 'w') as f:
        f.write(VALID_GTFS_FILE_CONTENT)


@pytest.fixture()
def empty_gtfs_file(tmp_path):
    """create an empty file for testing, delete it after test"""
    filepath = os.path.join(tmp_path, EMPTY_FILE)
    with open(filepath, 'w') as f:
        f.write('')


@pytest.fixture()
def not_existing_file(tmp_path):
    """delete file before testing if it exists"""
    filepath = os.path.join(tmp_path, NOT_EXISTING_FILE)
    try:
        os.remove(filepath)
    except FileNotFoundError:
        pass
