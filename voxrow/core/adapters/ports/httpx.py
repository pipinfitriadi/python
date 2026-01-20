#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 13 January 2026

from http import HTTPMethod
from typing import Optional, Union

from httpx import Response, get, post
from pydantic import HttpUrl, validate_call
from pydantic.dataclasses import dataclass

from ...domain.value_objects import Data
from . import AbstractSourcePort


@dataclass(frozen=True)
class HttpxSourcePort(AbstractSourcePort):
    url: HttpUrl
    method: HTTPMethod = HTTPMethod.GET
    headers: Optional[dict] = None
    json: Optional[dict] = None
    timeout: Optional[Union[float, int]] = None

    @validate_call
    def extract(self) -> Data:
        methods: dict = {
            HTTPMethod.GET: get,
            HTTPMethod.POST: post,
        }

        resp: Response = methods[self.method](
            url=str(self.url),
            **(dict(json=self.json) if self.method is HTTPMethod.POST else {}),
            headers=self.headers,
            **(dict(timeout=self.timeout) if self.timeout is not None else {}),
        )

        return resp.json()
