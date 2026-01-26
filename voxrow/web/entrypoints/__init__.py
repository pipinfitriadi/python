#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 25 January 2026

from functools import lru_cache

from ..domain.value_objects import Settings


@lru_cache
def get_settings() -> Settings:  # pragma: no cover
    return Settings()
