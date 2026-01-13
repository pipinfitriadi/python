#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 13 January 2026

from abc import ABC, abstractmethod

from pydantic import validate_call

from ...domain.value_objects import Data


class AbstractSourcePort(ABC):
    @abstractmethod
    @validate_call
    def fetch(self) -> Data:
        pass


class AbstractTransformPort(ABC):
    @abstractmethod
    @validate_call
    def enrich(self, data: Data) -> Data:
        pass


class AbstractDestinationPort(ABC):
    @abstractmethod
    @validate_call
    def load(self, data: Data) -> None:
        pass
