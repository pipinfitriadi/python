#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 26 January 2026

from datetime import datetime
from typing import Annotated

from typer import Argument, Option, Typer

from ..domain import value_objects

app: Typer = Typer(
    no_args_is_help=True,
    help=("\n" * 2).join(
        (
            f"{value_objects.TITLE} ({value_objects.VERSION})",
            f"{value_objects.AUTHOR} <{value_objects.EMAIL}>",
            str(value_objects.URL),
        )
    ),
)


@app.command()
def extract_bps_inflation() -> None:
    pass


@app.command()
def extract_idx_stock_summary(
    start_date: Annotated[datetime, Argument(formats=[value_objects.DATE_FMT])],
    end_date: Annotated[
        datetime | None,
        Option(formats=[value_objects.DATE_FMT]),
    ] = None,
) -> None:
    print(start_date.date(), end_date.date() if end_date else end_date)
