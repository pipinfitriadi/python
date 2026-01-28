#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 14 January 2026

from botocore.client import BaseClient
from pydantic import validate_call
from pydantic.dataclasses import dataclass

from ....core.adapters import ports
from ....core.domain import domain_services
from ....core.domain.value_objects import (
    CONFIG_DICT,
    ENCODING,
    ContentEncoding,
    ContentType,
    Data,
    ResourceLocation,
)
from ...domain.value_objects import Boto3Destination, Boto3Source


@dataclass(config=CONFIG_DICT, frozen=True)
class Boto3DataPort(ports.AbstractDataPort):
    client: BaseClient

    @validate_call
    async def extract(self, *, source: Boto3Source) -> Data:
        response: any = self.client.get_object(
            Bucket=source.bucket,
            Key=str(source.key),
            ChecksumMode="DISABLED",
        )
        data: bytes = response["Body"].read().decode(ENCODING)

        return (
            domain_services.loads_from_json(data)
            if response.get("ContentType") == ContentType.json
            else data
        )

    @validate_call
    async def load(
        self,
        data: Data,
        *,
        destination: Boto3Destination,
    ) -> ResourceLocation:
        data = (
            domain_services.dumps_to_json(data)
            if destination.content_type == ContentType.json
            else data
        )

        self.client.put_object(
            Bucket=destination.bucket,
            Key=str(destination.key),
            Body=(
                domain_services.compress_to_gzip(data)
                if destination.content_encoding == ContentEncoding.gzip
                else data
            ),
            **(
                dict(ContentEncoding=destination.content_encoding)
                if destination.content_encoding
                else {}
            ),
            ContentType=destination.content_type,
        )

        return destination.key
