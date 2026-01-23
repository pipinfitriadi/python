#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 14 January 2026

from types import TracebackType
from typing import Self

from pydantic import validate_call
from pydantic.dataclasses import dataclass

from ..adapters import ports
from ..domain.domain_services import Transform
from ..domain.value_objects import CONFIG_DICT, Data


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


# Implementations
@dataclass(config=CONFIG_DICT, frozen=True)
class EtlUnitOfWork(AbstractUnitOfWork):
    sources: tuple[Data | ports.AbstractSourcePort, ...]
    destination: ports.AbstractDestinationPort
    transform: Transform | None = None
