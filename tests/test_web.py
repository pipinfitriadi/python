#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 9 December 2025

from fastapi.testclient import TestClient
from httpx import Response

from voxrow.web import app

# Var
client: TestClient = TestClient(app)


def test_root() -> None:
    response: Response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}
