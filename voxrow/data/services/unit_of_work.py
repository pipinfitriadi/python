#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 25 January 2026

from boto3 import client
from botocore.client import BaseClient
from pydantic import validate_call

from ...core.services.unit_of_work import AbstractDataUnitOfWork
from ..adapters.ports import boto3
from ..domain.value_objects import Boto3Credential


class Boto3DataUnitOfWork(AbstractDataUnitOfWork):
    client: BaseClient

    @validate_call
    def __init__(self, credential: Boto3Credential) -> None:
        self.client = client(
            service_name=credential.service_name,
            endpoint_url=str(credential.endpoint_url),
            aws_access_key_id=credential.aws_access_key_id.get_secret_value(),
            aws_secret_access_key=credential.aws_secret_access_key.get_secret_value(),
            region_name=credential.region_name,
        )
        self.destination_port = boto3.Boto3DestinationPort(self.client)
        self.source_port = boto3.Boto3SourcePort(self.client)
