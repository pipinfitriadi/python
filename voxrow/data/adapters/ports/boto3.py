#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 14 January 2026

from pathlib import Path
from typing import Optional

from boto3 import client
from botocore.client import BaseClient
from pydantic import validate_call

from ....core.adapters import ports
from ....core.domain import domain_services
from ....core.domain.value_objects import (
    ENCODING,
    ContentEncoding,
    ContentType,
    Data,
    ResourceLocation,
)
from ...domain.value_objects import Boto3Credential


# Abstracts
class AbstractBoto3:
    client: BaseClient
    bucket: str
    key: Path

    @validate_call
    def __init__(
        self,
        credential: Boto3Credential,
        bucket: str,
        key: Path,
    ) -> None:
        self.client = client(
            service_name=credential.service_name,
            endpoint_url=str(credential.endpoint_url),
            aws_access_key_id=credential.aws_access_key_id.get_secret_value(),
            aws_secret_access_key=credential.aws_secret_access_key.get_secret_value(),
            region_name=credential.region_name,
        )
        self.bucket = bucket
        self.key = key


# Implementations
class Boto3SourcePort(AbstractBoto3, ports.AbstractSourcePort):
    @validate_call
    def extract(self) -> Data:
        response: any = self.client.get_object(
            Bucket=self.bucket,
            Key=str(self.key),
            ChecksumMode="DISABLED",
        )
        data: bytes = response["Body"].read().decode(ENCODING)

        return (
            domain_services.loads_from_json(data)
            if response.get("ContentType") == ContentType.json
            else data
        )


class Boto3DestinationPort(AbstractBoto3, ports.AbstractDestinationPort):
    content_encoding: ContentEncoding
    content_type: ContentType

    @validate_call
    def __init__(
        self,
        credential: Boto3Credential,
        bucket: str,
        key: Path,
        content_type: ContentType,
        content_encoding: Optional[ContentEncoding] = None,
    ) -> None:
        super().__init__(credential, bucket, key)

        self.content_type = content_type
        self.content_encoding = content_encoding

    @validate_call
    def load(self, data: Data) -> ResourceLocation:
        data = (
            domain_services.dumps_to_json(data)
            if self.content_type == ContentType.json
            else data
        )

        self.client.put_object(
            Bucket=self.bucket,
            Key=str(self.key),
            Body=(
                domain_services.compress_to_gzip(data)
                if self.content_encoding == ContentEncoding.gzip
                else data
            ),
            **(
                dict(ContentEncoding=self.content_encoding)
                if self.content_encoding
                else {}
            ),
            ContentType=self.content_type,
        )

        return self.key
