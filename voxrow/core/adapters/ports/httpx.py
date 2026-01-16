#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 13 January 2026

from httpx import Response, get
from pydantic import HttpUrl, validate_call
from pydantic.dataclasses import dataclass

from ...domain.value_objects import Data
from . import AbstractSourcePort


@dataclass(frozen=True)
class HttpxSourcePort(AbstractSourcePort):
    url: HttpUrl

    @validate_call
    def extract(self) -> Data:
        resp: Response = get(url=str(self.url))

        return resp.json()
