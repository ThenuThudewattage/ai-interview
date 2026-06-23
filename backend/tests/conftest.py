import os
import pytest

# Set env to testing to bypass startup db initialization
os.environ["APP_ENV"] = "testing"

from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
