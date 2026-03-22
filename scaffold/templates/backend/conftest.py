import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """FastAPI 测试客户端。"""
    with TestClient(app) as c:
        yield c
