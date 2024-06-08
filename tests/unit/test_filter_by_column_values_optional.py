import pandas as pd

from gtfs_filtering.core import filter_by_column_values_optional


def test_filter_by_column_values_optional__when_valid_column_and_values__returns_filtered_df():
    data = {"A": ["foo", "bar", "baz", "foo", None], "B": ["1", "2", "3", "4", "5"]}
    df = pd.DataFrame(data)
    accepted_values = ["foo", "baz"]

    result = filter_by_column_values_optional(df, "A", accepted_values)

    expected_data = {"A": ["foo", "baz", "foo", None], "B": ["1", "3", "4", "5"]}
    expected_index = [0, 2, 3, 4]
    expected_df = pd.DataFrame(expected_data, index=expected_index)

    pd.testing.assert_frame_equal(result, expected_df)


def test_filter_by_column_values_optional__when_column_not_in_df__returns_same_df():
    data = {"A": ["foo", "bar", "baz", "foo"], "B": ["1", "2", "3", "4"]}
    df = pd.DataFrame(data)
    accepted_values = ["foo", "baz"]

    result = filter_by_column_values_optional(df, "C", accepted_values)

    pd.testing.assert_frame_equal(df, result)


def test_filter_by_column_values_optional__when_no_accepted_values__returns_empty_or_nan_df():
    data = {"A": ["foo", "bar", "baz", "foo", None], "B": ["1", "2", "3", "4", "5"]}
    df = pd.DataFrame(data)
    accepted_values = []

    result = filter_by_column_values_optional(df, "A", accepted_values)

    expected_data = {"A": [None], "B": ["5"]}
    expected_index = [4]
    expected_df = pd.DataFrame(expected_data, index=expected_index)

    pd.testing.assert_frame_equal(result, expected_df)


def test_filter_by_column_values_optional__when_no_matching_values__returns_nan_df():
    data = {"A": ["foo", "bar", "baz", "foo", None], "B": ["1", "2", "3", "4", "5"]}
    df = pd.DataFrame(data)
    accepted_values = ["qux", "quux"]

    result = filter_by_column_values_optional(df, "A", accepted_values)

    expected_data = {"A": [None], "B": ["5"]}
    expected_index = [4]
    expected_df = pd.DataFrame(expected_data, index=expected_index)

    pd.testing.assert_frame_equal(result, expected_df)


def test_filter_by_column_values_optional__when_all_matching_values__returns_same_df():
    data = {"A": ["foo", "bar", "baz", "foo", None], "B": ["1", "2", "3", "4", "5"]}
    df = pd.DataFrame(data)
    accepted_values = ["foo", "bar", "baz"]

    result = filter_by_column_values_optional(df, "A", accepted_values)

    expected_df = df.copy()

    pd.testing.assert_frame_equal(result, expected_df)


def test_filter_by_column_values_optional__when_column_contains_nan__filters_correctly():
    data = {"A": ["foo", "bar", None, "baz", "foo"], "B": ["1", "2", "3", "4", "5"]}
    df = pd.DataFrame(data)
    accepted_values = ["foo", "baz"]

    result = filter_by_column_values_optional(df, "A", accepted_values)

    expected_data = {"A": ["foo", None, "baz", "foo"], "B": ["1", "3", "4", "5"]}
    expected_index = [0, 2, 3, 4]
    expected_df = pd.DataFrame(expected_data, index=expected_index)

    pd.testing.assert_frame_equal(result, expected_df)


def test_filter_by_column_values_optional__when_empty_dataframe__returns_empty_df():
    df = pd.DataFrame(columns=["A", "B"])
    accepted_values = ["foo", "baz"]

    result = filter_by_column_values_optional(df, "A", accepted_values)

    expected_df = pd.DataFrame(columns=["A", "B"])

    pd.testing.assert_frame_equal(result, expected_df)


def test_filter_by_column_values_optional__when_column_is_empty_string__filters_correctly():
    data = {"A": ["foo", "bar", "", "foo", None], "B": ["1", "2", "3", "4", "5"]}
    df = pd.DataFrame(data)
    accepted_values = ["foo"]

    result = filter_by_column_values_optional(df, "A", accepted_values)

    expected_data = {"A": ["foo", "foo", None], "B": ["1", "4", "5"]}
    expected_index = [0, 3, 4]
    expected_df = pd.DataFrame(expected_data, index=expected_index)

    pd.testing.assert_frame_equal(result, expected_df)


def test_filter_by_column_values_optional__when_column_is_boolean_string__filters_correctly():
    data = {"A": ["True", "False", "True", None], "B": ["1", "2", "3", "4"]}
    df = pd.DataFrame(data)
    accepted_values = ["True"]

    result = filter_by_column_values_optional(df, "A", accepted_values)

    expected_data = {"A": ["True", "True", None], "B": ["1", "3", "4"]}
    expected_index = [0, 2, 3]
    expected_df = pd.DataFrame(expected_data, index=expected_index)

    pd.testing.assert_frame_equal(result, expected_df)
