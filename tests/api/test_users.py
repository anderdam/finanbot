import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_register_and_login(async_client: AsyncClient):
    # async_client fixture should mount the app and provide isolated test DB
    payload = {"email": "alice@example.com", "password": "s3cur3pass", "full_name": "Alice"}
    r = await async_client.post("/v1/users/register", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "alice@example.com"

    # login via OAuth2PasswordRequestForm (username=password fields)
    r2 = await async_client.post("/v1/users/login", data={"username": "alice@example.com", "password": "s3cur3pass"})
    assert r2.status_code == 200
    token = r2.json()["access_token"]
    assert token
