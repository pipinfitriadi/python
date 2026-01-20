#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 13 January 2026

from enum import StrEnum
from pathlib import Path
from typing import Any, Dict, Iterator, TypeAlias, Union

from pydantic import ConfigDict, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

# Constants
CONFIG_DICT = ConfigDict(arbitrary_types_allowed=True)

ResourceLocation: TypeAlias = Path
Row: TypeAlias = Dict[str, Any]


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
            ]
        )


Data: TypeAlias = Union[Rows, Any]


class ContentType(StrEnum):
    html = "text/html"
    json = "application/json"
    svg = "image/svg+xml"
    xml = "application/xml"
