#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 26 January 2026

from datetime import date, datetime
from functools import lru_cache

from ...data.domain import value_objects
from .value_objects import Settings


@lru_cache
def get_fastapi_settings() -> Settings:  # pragma: no cover
    return Settings()


def get_typer_settings() -> Settings:  # pragma: no cover
    return Settings(_env_file=".env")


def today() -> date:
    return datetime.now(tz=value_objects.TIME_ZONE).date()
