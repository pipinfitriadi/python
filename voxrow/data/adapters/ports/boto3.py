#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 14 January 2026

import json
from pathlib import Path

from boto3 import client
from botocore.client import BaseClient
from pydantic import validate_call

from ....core.adapters import ports
from ....core.domain.value_objects import ContentType, Data, ResourceLocation
from ...domain.value_objects import ENCODING, Boto3Credential, Boto3Object


# Abstracts
class AbstractBoto3:
    client: BaseClient
    bucket: str

    @validate_call
    def __init__(
        self,
        credential: Boto3Credential,
        bucket: str,
    ) -> None:
        self.client = client(
            service_name=credential.service_name,
            endpoint_url=str(credential.endpoint_url),
            aws_access_key_id=credential.aws_access_key_id.get_secret_value(),
            aws_secret_access_key=credential.aws_secret_access_key.get_secret_value(),
            region_name=credential.region_name,
        )
        self.bucket = bucket


# Implementations
class Boto3SourcePort(AbstractBoto3, ports.AbstractSourcePort):
    key: Path

    @validate_call
    def __init__(
        self,
        credential: Boto3Credential,
        bucket: str,
        key: Path,
    ) -> None:
        super().__init__(credential, bucket)

        self.key = key

    @validate_call
    def extract(self) -> Data:
        data: Data = (
            self.client.get_object(
                Bucket=self.bucket,
                Key=str(self.key),
            )["Body"]
            .read()
            .decode(ENCODING)
        )

        return (
            json.loads(data)
            if self.key.suffix
            and f"application/{self.key.suffix[1:].lower()}" == ContentType.json
            else data
        )


class Boto3DestinationPort(AbstractBoto3, ports.AbstractDestinationPort):
    boto3_object: Boto3Object

    @validate_call
    def __init__(
        self,
        credential: Boto3Credential,
        bucket: str,
        boto3_object: Boto3Object,
    ) -> None:
        super().__init__(credential, bucket)

        self.boto3_object = boto3_object

    @validate_call
    def load(self, data: Data) -> ResourceLocation:
        self.client.put_object(
            Bucket=self.bucket,
            Key=str(self.boto3_object.key),
            Body=(
                json.dumps(data, default=str)
                if self.boto3_object.content_type == ContentType.json
                else data
            ),
            ContentType=self.boto3_object.content_type,
        )

        return self.boto3_object.key
