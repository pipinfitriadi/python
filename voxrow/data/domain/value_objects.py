#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 14 January 2026

from datetime import date, datetime
from pathlib import Path
from typing import Annotated, TypeAlias
from zoneinfo import ZoneInfo

from pydantic import Field, HttpUrl, SecretStr
from pydantic.dataclasses import dataclass
from pydantic_settings import BaseSettings, SettingsConfigDict

from ...core.domain.value_objects import (
    ContentEncoding,
    ContentType,
    Destination,
    Source,
)

# Constants
TIME_ZONE: ZoneInfo = ZoneInfo("Asia/Jakarta")

Date: TypeAlias = Annotated[
    date,
    Field(default_factory=lambda: datetime.now(tz=TIME_ZONE).date),
]


@dataclass(frozen=True)
class Boto3Credential:
    endpoint_url: HttpUrl
    aws_access_key_id: SecretStr
    aws_secret_access_key: SecretStr
    region_name: str = "auto"
    service_name: str = "s3"


@dataclass(frozen=True)
class Boto3Source(Source):
    bucket: str
    key: Path


@dataclass(frozen=True)
class Boto3Destination(Destination, Boto3Source):
    content_type: ContentType
    content_encoding: ContentEncoding | None = None


class Settings(BaseSettings):
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_nested_delimiter="__",
        frozen=True,
    )

    bps_key: SecretStr
    cloudflare_r2: Boto3Credential
    decodo_web_scraping_token: SecretStr
