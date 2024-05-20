import pandas as pd
import pytest

from gtfs_filtering.core import filter_by_column_values


def test_filter_by_column_values__when_valid_column_and_values__returns_filtered_df():
    data = {
        'A': ['foo', 'bar', 'baz', 'foo'],
        'B': [1, 2, 3, 4]
    }
    df = pd.DataFrame(data, dtype=str)
    accepted_values = ['foo', 'baz']

    result = filter_by_column_values(df, 'A', accepted_values)

    expected_data = {
        'A': ['foo', 'baz', 'foo'],
        'B': [1, 3, 4]
    }
    expected_df = pd.DataFrame(expected_data, index=[0, 2, 3], dtype=str)

    pd.testing.assert_frame_equal(result, expected_df)


def test_filter_by_column_values__when_column_not_in_df__raises_key_error():
    data = {
        'A': ['foo', 'bar', 'baz', 'foo'],
        'B': [1, 2, 3, 4]
    }
    df = pd.DataFrame(data, dtype=str)
    accepted_values = ['foo', 'baz']

    with pytest.raises(KeyError):
        filter_by_column_values(df, 'C', accepted_values)


def test_filter_by_column_values__when_no_accepted_values__returns_empty_df():
    data = {
        'A': ['foo', 'bar', 'baz', 'foo'],
        'B': [1, 2, 3, 4]
    }
    df = pd.DataFrame(data, dtype=str)
    accepted_values = []

    result = filter_by_column_values(df, 'A', accepted_values)

    expected_df = pd.DataFrame({'A': [], 'B': []}, dtype=str)

    pd.testing.assert_frame_equal(result, expected_df)


def test_filter_by_column_values__when_no_matching_values__returns_empty_df():
    data = {
        'A': ['foo', 'bar', 'baz', 'foo'],
        'B': [1, 2, 3, 4]
    }
    df = pd.DataFrame(data, dtype=str)
    accepted_values = ['qux', 'quux']

    result = filter_by_column_values(df, 'A', accepted_values)

    expected_df = pd.DataFrame(columns=['A', 'B'], dtype=str)

    pd.testing.assert_frame_equal(result, expected_df)


def test_filter_by_column_values__when_all_matching_values__returns_same_df():
    data = {
        'A': ['foo', 'bar', 'baz', 'foo'],
        'B': [1, 2, 3, 4]
    }
    df = pd.DataFrame(data, dtype=str)
    accepted_values = ['foo', 'bar', 'baz']

    result = filter_by_column_values(df, 'A', accepted_values)

    pd.testing.assert_frame_equal(result, df)


def test_filter_by_column_values__when_column_contains_nan__filters_correctly():
    data = {
        'A': ['foo', 'bar', None, 'baz', 'foo'],
        'B': [1, 2, 3, 4, 5]
    }
    df = pd.DataFrame(data, dtype=str)
    accepted_values = ['foo', 'baz']

    result = filter_by_column_values(df, 'A', accepted_values)

    expected_data = {
        'A': ['foo', 'baz', 'foo'],
        'B': [1, 4, 5]
    }
    expected_df = pd.DataFrame(expected_data, index=[0, 3, 4], dtype=str)

    pd.testing.assert_frame_equal(result, expected_df)


def test_filter_by_column_values__when_empty_dataframe__returns_empty_df():
    df = pd.DataFrame(columns=['A', 'B'], dtype=str)
    accepted_values = ['foo', 'baz']

    result = filter_by_column_values(df, 'A', accepted_values)

    expected_df = pd.DataFrame(columns=['A', 'B'], dtype=str)

    pd.testing.assert_frame_equal(result, expected_df)


def test_filter_by_column_values__when_column_is_numeric__filters_correctly():
    data = {
        'A': [1, 2, 3, 1, 4],
        'B': [10, 20, 30, 40, 50]
    }
    df = pd.DataFrame(data, dtype=str)
    accepted_values = ['1', '3']

    result = filter_by_column_values(df, 'A', accepted_values)

    expected_data = {
        'A': [1, 3, 1],
        'B': [10, 30, 40]
    }
    expected_df = pd.DataFrame(expected_data, index=[0, 2, 3], dtype=str)

    pd.testing.assert_frame_equal(result, expected_df)
