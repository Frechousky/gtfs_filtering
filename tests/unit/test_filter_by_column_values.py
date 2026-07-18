import pytest

from gtfs_filtering.core import filter_by_column_values
from tests.unit.conftest import make_relation, relations_equal


def test_filter_by_column_values__when_valid_column_and_values__returns_filtered_df():
    rel = make_relation({"A": ["foo", "bar", "baz", "foo"], "B": ["1", "2", "3", "4"]})
    accepted_values = ["foo", "baz"]

    result = filter_by_column_values(rel, "A", accepted_values)

    expected = make_relation({"A": ["foo", "baz", "foo"], "B": ["1", "3", "4"]})
    assert relations_equal(result, expected)


def test_filter_by_column_values__when_column_not_in_df__raises_key_error():
    rel = make_relation({"A": ["foo", "bar", "baz", "foo"], "B": ["1", "2", "3", "4"]})
    accepted_values = ["foo", "baz"]

    with pytest.raises(KeyError):
        filter_by_column_values(rel, "C", accepted_values)


def test_filter_by_column_values__when_no_accepted_values__returns_empty_df():
    rel = make_relation({"A": ["foo", "bar", "baz", "foo"], "B": ["1", "2", "3", "4"]})
    accepted_values = []

    result = filter_by_column_values(rel, "A", accepted_values)

    expected = make_relation({"A": [], "B": []})
    assert relations_equal(result, expected)


def test_filter_by_column_values__when_no_matching_values__returns_empty_df():
    rel = make_relation({"A": ["foo", "bar", "baz", "foo"], "B": ["1", "2", "3", "4"]})
    accepted_values = ["qux", "quux"]

    result = filter_by_column_values(rel, "A", accepted_values)

    expected = make_relation({"A": [], "B": []})
    assert relations_equal(result, expected)


def test_filter_by_column_values__when_all_matching_values__returns_same_df():
    rel = make_relation({"A": ["foo", "bar", "baz", "foo"], "B": ["1", "2", "3", "4"]})
    accepted_values = ["foo", "bar", "baz"]

    result = filter_by_column_values(rel, "A", accepted_values)

    assert relations_equal(result, rel)


def test_filter_by_column_values__when_column_contains_nan__filters_correctly():
    rel = make_relation(
        {"A": ["foo", "bar", None, "baz", "foo"], "B": ["1", "2", "3", "4", "5"]}
    )
    accepted_values = ["foo", "baz"]

    result = filter_by_column_values(rel, "A", accepted_values)

    expected = make_relation({"A": ["foo", "baz", "foo"], "B": ["1", "4", "5"]})
    assert relations_equal(result, expected)


def test_filter_by_column_values__when_empty_dataframe__returns_empty_df():
    rel = make_relation({"A": [], "B": []})
    accepted_values = ["foo", "baz"]

    result = filter_by_column_values(rel, "A", accepted_values)

    expected = make_relation({"A": [], "B": []})
    assert relations_equal(result, expected)


def test_filter_by_column_values__when_column_is_numeric__filters_correctly():
    rel = make_relation(
        {"A": ["1", "2", "3", "1", "4"], "B": ["10", "20", "30", "40", "50"]}
    )
    accepted_values = ["1", "3"]

    result = filter_by_column_values(rel, "A", accepted_values)

    expected = make_relation({"A": ["1", "3", "1"], "B": ["10", "30", "40"]})
    assert relations_equal(result, expected)
