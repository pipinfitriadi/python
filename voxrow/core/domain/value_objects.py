#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 13 January 2026

from collections.abc import Iterator
from enum import StrEnum
from http import HTTPMethod
from pathlib import Path
from ssl import SSLContext
from typing import Any

from pydantic import ConfigDict, GetCoreSchemaHandler, HttpUrl
from pydantic.dataclasses import dataclass
from pydantic_core import CoreSchema, core_schema

# Constants
CONFIG_DICT = ConfigDict(arbitrary_types_allowed=True)
ENCODING: str = "utf-8"

type ResourceLocation = Path
type Row = dict[str, Any]


class Rows(Iterator[Row]):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.chain_schema(
            [
                core_schema.is_instance_schema(Iterator),
                core_schema.generator_schema(handler.generate_schema(Row)),
            ],
        )


type Data = Rows | Any


class ContentEncoding(StrEnum):
    gzip = "gzip"


class ContentType(StrEnum):
    html = "text/html"
    json = "application/json"
    svg = "image/svg+xml"
    xml = "application/xml"


@dataclass(frozen=True)
class Destination: ...


@dataclass(frozen=True)
class Source: ...


@dataclass(frozen=True)
class PathDestination(Destination):
    file: Path


@dataclass(config=CONFIG_DICT, frozen=True)
class HttpxSource(Source):
    url: HttpUrl
    method: HTTPMethod = HTTPMethod.GET
    headers: dict | None = None
    json: Any | None = None
    timeout: float | None = None
    verify: SSLContext | str | bool = True
