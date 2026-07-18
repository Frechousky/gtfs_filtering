from gtfs_filtering.core import filter_by_column_values_optional
from tests.unit.conftest import make_relation, relations_equal


def test_filter_by_column_values_optional__when_valid_column_and_values__returns_filtered_df():
    rel = make_relation(
        {"A": ["foo", "bar", "baz", "foo", None], "B": ["1", "2", "3", "4", "5"]}
    )
    accepted_values = ["foo", "baz"]

    result = filter_by_column_values_optional(rel, "A", accepted_values)

    expected = make_relation(
        {"A": ["foo", "baz", "foo", None], "B": ["1", "3", "4", "5"]}
    )
    assert relations_equal(result, expected)


def test_filter_by_column_values_optional__when_column_not_in_df__returns_same_df():
    rel = make_relation({"A": ["foo", "bar", "baz", "foo"], "B": ["1", "2", "3", "4"]})
    accepted_values = ["foo", "baz"]

    result = filter_by_column_values_optional(rel, "C", accepted_values)

    assert relations_equal(rel, result)


def test_filter_by_column_values_optional__when_no_accepted_values__returns_empty_or_nan_df():
    rel = make_relation(
        {"A": ["foo", "bar", "baz", "foo", None], "B": ["1", "2", "3", "4", "5"]}
    )
    accepted_values = []

    result = filter_by_column_values_optional(rel, "A", accepted_values)

    expected = make_relation({"A": [None], "B": ["5"]})
    assert relations_equal(result, expected)


def test_filter_by_column_values_optional__when_no_matching_values__returns_nan_df():
    rel = make_relation(
        {"A": ["foo", "bar", "baz", "foo", None], "B": ["1", "2", "3", "4", "5"]}
    )
    accepted_values = ["qux", "quux"]

    result = filter_by_column_values_optional(rel, "A", accepted_values)

    expected = make_relation({"A": [None], "B": ["5"]})
    assert relations_equal(result, expected)


def test_filter_by_column_values_optional__when_all_matching_values__returns_same_df():
    rel = make_relation(
        {"A": ["foo", "bar", "baz", "foo", None], "B": ["1", "2", "3", "4", "5"]}
    )
    accepted_values = ["foo", "bar", "baz"]

    result = filter_by_column_values_optional(rel, "A", accepted_values)

    assert relations_equal(result, rel)


def test_filter_by_column_values_optional__when_column_contains_nan__filters_correctly():
    rel = make_relation(
        {"A": ["foo", "bar", None, "baz", "foo"], "B": ["1", "2", "3", "4", "5"]}
    )
    accepted_values = ["foo", "baz"]

    result = filter_by_column_values_optional(rel, "A", accepted_values)

    expected = make_relation(
        {"A": ["foo", None, "baz", "foo"], "B": ["1", "3", "4", "5"]}
    )
    assert relations_equal(result, expected)


def test_filter_by_column_values_optional__when_empty_dataframe__returns_empty_df():
    rel = make_relation({"A": [], "B": []})
    accepted_values = ["foo", "baz"]

    result = filter_by_column_values_optional(rel, "A", accepted_values)

    expected = make_relation({"A": [], "B": []})
    assert relations_equal(result, expected)


def test_filter_by_column_values_optional__when_column_is_empty_string__filters_correctly():
    rel = make_relation(
        {"A": ["foo", "bar", "", "foo", None], "B": ["1", "2", "3", "4", "5"]}
    )
    accepted_values = ["foo"]

    result = filter_by_column_values_optional(rel, "A", accepted_values)

    expected = make_relation({"A": ["foo", "foo", None], "B": ["1", "4", "5"]})
    assert relations_equal(result, expected)


def test_filter_by_column_values_optional__when_column_is_boolean_string__filters_correctly():
    rel = make_relation(
        {"A": ["True", "False", "True", None], "B": ["1", "2", "3", "4"]}
    )
    accepted_values = ["True"]

    result = filter_by_column_values_optional(rel, "A", accepted_values)

    expected = make_relation({"A": ["True", "True", None], "B": ["1", "3", "4"]})
    assert relations_equal(result, expected)
