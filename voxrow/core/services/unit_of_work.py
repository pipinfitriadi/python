#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 14 January 2026

from copy import copy
from types import TracebackType
from typing import Self

from pydantic import validate_call

from ..adapters import ports
from ..adapters.ports import httpx, pathlib
from ..domain.value_objects import CONFIG_DICT, Destination, Source


# Abstracts
class AbstractUnitOfWork:  # pragma: no cover
    def __enter__(self) -> Self:
        return self

    @validate_call(config=CONFIG_DICT)
    def exc_handle(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: TracebackType,
    ) -> bool:
        return False

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass

    @validate_call(config=CONFIG_DICT)
    def __exit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        exc_traceback: TracebackType | None = None,
    ) -> bool | None:
        is_exc_suppresses: bool = False

        if exc_type:
            self.rollback()

            is_exc_suppresses = self.exc_handle(exc_type, exc_value, exc_traceback)
        else:
            self.commit()

        return is_exc_suppresses


class AbstractDataUnitOfWork(AbstractUnitOfWork):  # pragma: no cover
    destination_domain: Destination | None = None
    destination_port: ports.AbstractDestinationPort | None = None
    source_domain: Source | None = None
    source_port: ports.AbstractSourcePort | None = None

    @validate_call
    def __call__(
        self,
        *,
        source: Source | None = None,
        destination: Destination | None = None,
    ) -> Self:
        self.source_domain = source
        self.destination_domain = destination

        return copy(self)

    def __enter__(self) -> Self:
        if not any((self.source_domain, self.destination_domain)):
            raise ValueError("destination_domain or source_domain must not be empty")

        return super().__enter__()

    @validate_call(config=CONFIG_DICT)
    def __exit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        exc_traceback: TracebackType | None = None,
    ) -> bool | None:
        self.source_domain = None
        self.destination_domain = None

        return super().__exit__(exc_type, exc_value, exc_traceback)


# Implementations
class HttpxDataUnitOfWork(AbstractDataUnitOfWork):
    def __init__(self) -> None:
        self.source_port = httpx.HttpxSourcePort()


class PathDataUnitOfWork(AbstractDataUnitOfWork):
    def __init__(self) -> None:
        self.destination_port = pathlib.PathDestinationPort()
