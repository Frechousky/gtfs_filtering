#!/usr/bin/env python3
import typing

import click

from gtfs_filtering.core import perform_filter, FilterType


@click.command()
@click.option(
    "-o",
    "--overwrite",
    is_flag=True,
    default=False,
    help="pass it to overwrite output GTFS zip if it exists",
)
@click.option(
    "-t",
    "--filter-type",
    type=click.Choice([f_type.value for f_type in FilterType]),
    default=FilterType.ROUTE_ID.value,
    help="type of filtering",
)
@click.argument("input_gtfs_zip", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_gtfs_zip", type=click.Path(dir_okay=False))
@click.argument("filter_values", nargs=-1, required=True)
def cli(
    overwrite: bool,
    filter_type: str,
    input_gtfs_zip: str,
    output_gtfs_zip: str,
    filter_values: typing.List[str],
):
    try:
        perform_filter(
            input_gtfs_zip,
            output_gtfs_zip,
            FilterType(filter_type),
            filter_values,
            overwrite,
        )
    except (FileExistsError, FileNotFoundError, PermissionError, ValueError) as e:
        raise click.ClickException(str(e))


if __name__ == "__main__":
    cli()
