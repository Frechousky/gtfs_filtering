#!/usr/bin/env python3
from typing import List

from click import command, option, argument, Choice, Path
from gtfs_filtering.core import perform_filter, FilterType


@command()
@option('-o', '--overwrite', is_flag=True, default=False,
              help='pass it to overwrite output GTFS zip if it exists')
@option('-t', '--filter-type', type=Choice([f_type.value for f_type in FilterType]),
              default=FilterType.ROUTE_ID.value, help='type of filtering')
@argument('input_gtfs_zip', type=Path(exists=True, dir_okay=False))
@argument('output_gtfs_zip', type=Path(dir_okay=False))
@argument('filter_values', nargs=-1, required=True)
def cli(overwrite: bool, filter_type: str, input_gtfs_zip: str, output_gtfs_zip: str,
        filter_values: List[str]):
    perform_filter(input_gtfs_zip, output_gtfs_zip, FilterType(filter_type), filter_values, overwrite)


if __name__ == '__main__':
    cli()
