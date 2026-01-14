#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 14 January 2026

from pathlib import Path

from pydantic import HttpUrl, SecretStr
from pydantic.dataclasses import dataclass

# Constants
ENCODING: str = "utf-8"


@dataclass
class Boto3Credential:
    endpoint_url: HttpUrl
    aws_access_key_id: SecretStr
    aws_secret_access_key: SecretStr
    region_name: str = "auto"
    service_name: str = "s3"


@dataclass
class Boto3Object:
    key: Path
    content_type: str
