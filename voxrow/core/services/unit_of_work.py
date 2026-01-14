#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 14 January 2026

from types import TracebackType
from typing import Optional, Self, Tuple

from pydantic import BaseModel, validate_call

from ..adapters import ports
from ..domain.domain_services import Transform
from ..domain.value_objects import CONFIG_DICT


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
        exc_type: Optional[type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        exc_traceback: Optional[TracebackType] = None,
    ) -> Optional[bool]:
        is_exc_suppresses: bool = False

        if exc_type:
            self.rollback()

            is_exc_suppresses = self.exc_handle(exc_type, exc_value, exc_traceback)
        else:
            self.commit()

        return is_exc_suppresses


# Implementations
class EtlUnitOfWork(BaseModel, AbstractUnitOfWork):
    model_config = CONFIG_DICT

    sources: Tuple[ports.AbstractSourcePort, ...]
    destination: ports.AbstractDestinationPort
    transform: Optional[Transform]
