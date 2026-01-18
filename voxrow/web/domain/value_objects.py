#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 31 December 2025

from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from ...data.domain import value_objects

# Constants
ROOT_DIR: Path = Path("voxrow") / "web"
STATIC_DIR: Path = ROOT_DIR / "static"


class Settings(BaseSettings):
    model_config: SettingsConfigDict = SettingsConfigDict(env_nested_delimiter="__")

    bps_key: SecretStr
    cloudflare_r2: value_objects.Boto3Credential
    cron_secret: SecretStr
