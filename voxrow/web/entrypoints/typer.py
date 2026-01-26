#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 26 January 2026

import asyncio
from datetime import datetime
from typing import Annotated

from typer import Option, Typer

from ...data.services import handlers
from ..domain import domain_services, value_objects

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
    asyncio.run(handlers.extract_bps_inflation(domain_services.get_typer_settings()))


@app.command()
def extract_idx_stock_summary(
    start_date: Annotated[
        datetime,
        Option(
            formats=[value_objects.DATE_FMT],
            default_factory=lambda: domain_services.today().isoformat(),
        ),
    ],
    end_date: Annotated[
        datetime | None,
        Option(formats=[value_objects.DATE_FMT]),
    ] = None,
) -> None:
    asyncio.run(
        handlers.extract_idx_stock_summary(
            settings=domain_services.get_typer_settings(),
            start_date=start_date,
            end_date=end_date,
        )
    )
