#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 31 December 2025

from enum import StrEnum
from pathlib import Path

# Constants
ENCODING: str = "utf-8"
ROOT_DIR: Path = Path("voxrow") / "web"
STATIC_DIR: Path = ROOT_DIR / "static"


class ContentType(StrEnum):
    html = "text/html"
    svg = "image/svg+xml"
    xml = "application/xml"
