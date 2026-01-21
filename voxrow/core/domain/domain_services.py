#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 14 January 2026

import gzip
import json
from typing import Protocol, runtime_checkable

from pydantic import validate_call

from .value_objects import ENCODING, Data


@runtime_checkable
class Transform(Protocol):
    @validate_call
    def __call__(self, *args: Data) -> Data: ...


@validate_call
def compress_to_gzip(*args: Data) -> Data:
    data: Data = args[0]

    if not isinstance(data, str) and not isinstance(data, bytes):
        data: str = str(data)

    if not isinstance(data, bytes):
        data: bytes = data.encode(ENCODING)

    return gzip.compress(data, compresslevel=9)


@validate_call
def decompress_from_gzip(*args: Data) -> Data:
    return gzip.decompress(args[0])


@validate_call
def dumps_to_json(*args: Data) -> Data:
    return json.dumps(args[0], default=str)


@validate_call
def loads_from_json(*args: Data) -> Data:
    return json.loads(args[0])
