#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 26 January 2026

from typer import Typer

from ..domain import value_objects

app: Typer = Typer(
    no_args_is_help=True,
    help=("\n" * 2).join(
        [
            f"{value_objects.TITLE} ({value_objects.VERSION})",
            f"{value_objects.AUTHOR} <{value_objects.EMAIL}>",
            str(value_objects.URL),
        ]
    ),
)


@app.command()
def tes() -> None:
    pass


@app.command()
def tus() -> None:
    pass
