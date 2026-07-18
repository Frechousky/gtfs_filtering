import pytest

from gtfs_filtering.core import get_unique_not_null_column_values
from tests.unit.conftest import make_relation


def test_get_unique_not_null_column_values__when_column_exists_and_has_non_null_values__returns_unique_values():
    rel = make_relation(
        {
            "A": ["foo", "bar", "foo", "baz", "bar", None],
            "B": ["1", "2", "3", "4", "5", "6"],
        }
    )

    result = get_unique_not_null_column_values(rel, "A")
    expected = ["foo", "bar", "baz"]

    assert set(result) == set(expected)


def test_get_unique_not_null_column_values__when_column_exists_and_all_values_are_null__returns_empty_list():
    rel = make_relation({"A": [None, None, None], "B": ["1", "2", "3"]})

    result = get_unique_not_null_column_values(rel, "A")
    expected = []

    assert result == expected


def test_get_unique_not_null_column_values__when_column_does_not_exist__raises_key_error():
    rel = make_relation({"A": ["foo", "bar", "baz"], "B": ["1", "2", "3"]})

    with pytest.raises(KeyError):
        get_unique_not_null_column_values(rel, "C")


def test_get_unique_not_null_column_values__when_column_is_empty__returns_empty_list():
    rel = make_relation({"A": [], "B": []})

    result = get_unique_not_null_column_values(rel, "A")
    expected = []

    assert result == expected


def test_get_unique_not_null_column_values__when_column_has_mixed_types__returns_unique_non_null_values():
    rel = make_relation(
        {
            "A": ["foo", "1", "bar", "2.5", None, "foo", "1"],
            "B": ["1", "2", "3", "4", "5", "6", "7"],
        }
    )

    result = get_unique_not_null_column_values(rel, "A")
    expected = ["foo", "1", "bar", "2.5"]

    assert set(result) == set(expected)


def test_get_unique_not_null_column_values__when_column_has_all_unique_non_null_values__returns_all_values():
    rel = make_relation({"A": ["foo", "bar", "baz", "qux"], "B": ["1", "2", "3", "4"]})

    result = get_unique_not_null_column_values(rel, "A")
    expected = ["foo", "bar", "baz", "qux"]

    assert set(result) == set(expected)


def test_get_unique_not_null_column_values__when_column_has_duplicates_and_nulls__returns_unique_non_null_values():
    rel = make_relation(
        {
            "A": ["foo", "bar", None, "foo", "baz", None, "bar"],
            "B": ["1", "2", "3", "4", "5", "6", "7"],
        }
    )

    result = get_unique_not_null_column_values(rel, "A")
    expected = ["foo", "bar", "baz"]

    assert set(result) == set(expected)
