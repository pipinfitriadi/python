#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 21 January 2026

import gzip
from pathlib import Path
from tempfile import NamedTemporaryFile

from pytest import fixture

from voxrow.core.domain import domain_services
from voxrow.core.domain.value_objects import ENCODING, PathDestination
from voxrow.core.services import unit_of_work

# Constants
TEST_DATA_FOR_GZIP: tuple = (1, 2, 3)
TEST_DATA_FOR_GZIP_BYTES: bytes = str(TEST_DATA_FOR_GZIP).encode(ENCODING)


@fixture
def fake_gzip() -> bytes:
    return gzip.compress(TEST_DATA_FOR_GZIP_BYTES, compresslevel=9)


# Domain > Domain Services
def test_compress_to_gzip(fake_gzip: bytes) -> None:
    assert domain_services.compress_to_gzip(*(TEST_DATA_FOR_GZIP,)) == fake_gzip


def test_decompress_from_gzip(fake_gzip: bytes) -> None:
    assert domain_services.decompress_from_gzip(fake_gzip) == TEST_DATA_FOR_GZIP_BYTES


# Unit of Work > Data > Path
def test_path_data_unit_of_work() -> None:
    with (
        unit_of_work.PathDataUnitOfWork() as uow,
        NamedTemporaryFile(mode="w+", suffix=".txt") as temp_file,
    ):
        data: str = "Test"
        file_path: Path = uow.destination.load(
            data,
            destination=PathDestination(temp_file.name),
        )

        assert file_path.read_text() == data
        assert file_path == Path(temp_file.name)
