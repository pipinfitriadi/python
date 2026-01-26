#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 31 December 2025

from importlib.metadata import PackageMetadata, metadata, version
from pathlib import Path

from pydantic import EmailStr, HttpUrl, SecretStr

from ...data.domain import value_objects

# Constants
TITLE: str = "VOXROW"
DISTRIBUTION_NAME: str = "voxrow.web"
VERSION: str = version(DISTRIBUTION_NAME)
METADATA: PackageMetadata = metadata(DISTRIBUTION_NAME)
LICENSE: str = METADATA.get("license")
AUTHOR: str = METADATA.get("Author")
EMAIL: EmailStr = METADATA.get("Author-email")
URL: HttpUrl = HttpUrl(METADATA.get_all("Project-URL")[0].split(", ")[1])
ROOT_DIR: Path = Path("voxrow") / "web"
STATIC_DIR: Path = ROOT_DIR / "static"


class Settings(value_objects.Settings):
    cron_secret: SecretStr
