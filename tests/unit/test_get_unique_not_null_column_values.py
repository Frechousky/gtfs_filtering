import pandas as pd
import pytest

from gtfs_filtering.core import get_unique_not_null_column_values


def test_get_unique_not_null_column_values__when_column_exists_and_has_non_null_values__returns_unique_values():
    data = {
        "A": ["foo", "bar", "foo", "baz", "bar", None],
        "B": ["1", "2", "3", "4", "5", "6"],
    }
    df = pd.DataFrame(data)

    result = get_unique_not_null_column_values(df, "A")
    expected = ["foo", "bar", "baz"]

    assert set(result) == set(expected)


def test_get_unique_not_null_column_values__when_column_exists_and_all_values_are_null__returns_empty_list():
    data = {"A": [None, None, None], "B": ["1", "2", "3"]}
    df = pd.DataFrame(data)

    result = get_unique_not_null_column_values(df, "A")
    expected = []

    assert result == expected


def test_get_unique_not_null_column_values__when_column_does_not_exist__raises_key_error():
    data = {"A": ["foo", "bar", "baz"], "B": ["1", "2", "3"]}
    df = pd.DataFrame(data)

    with pytest.raises(KeyError):
        get_unique_not_null_column_values(df, "C")


def test_get_unique_not_null_column_values__when_column_is_empty__returns_empty_list():
    data = {"A": [], "B": []}
    df = pd.DataFrame(data)

    result = get_unique_not_null_column_values(df, "A")
    expected = []

    assert result == expected


def test_get_unique_not_null_column_values__when_column_has_mixed_types__returns_unique_non_null_values():
    data = {
        "A": ["foo", 1, "bar", 2.5, None, "foo", 1],
        "B": ["1", "2", "3", "4", "5", "6", "7"],
    }
    df = pd.DataFrame(data)

    result = get_unique_not_null_column_values(df, "A")
    expected = ["foo", 1, "bar", 2.5]

    assert set(result) == set(expected)


def test_get_unique_not_null_column_values__when_column_has_all_unique_non_null_values__returns_all_values():
    data = {"A": ["foo", "bar", "baz", "qux"], "B": ["1", "2", "3", "4"]}
    df = pd.DataFrame(data)

    result = get_unique_not_null_column_values(df, "A")
    expected = ["foo", "bar", "baz", "qux"]

    assert set(result) == set(expected)


def test_get_unique_not_null_column_values__when_column_has_duplicates_and_nulls__returns_unique_non_null_values():
    data = {
        "A": ["foo", "bar", None, "foo", "baz", None, "bar"],
        "B": ["1", "2", "3", "4", "5", "6", "7"],
    }
    df = pd.DataFrame(data)

    result = get_unique_not_null_column_values(df, "A")
    expected = ["foo", "bar", "baz"]

    assert set(result) == set(expected)
