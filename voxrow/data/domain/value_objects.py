#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 14 January 2026

from zoneinfo import ZoneInfo

from pydantic import HttpUrl, SecretStr
from pydantic.dataclasses import dataclass

# Constants
TIME_ZONE: ZoneInfo = ZoneInfo("Asia/Jakarta")


@dataclass(frozen=True)
class Boto3Credential:
    endpoint_url: HttpUrl
    aws_access_key_id: SecretStr
    aws_secret_access_key: SecretStr
    region_name: str = "auto"
    service_name: str = "s3"
