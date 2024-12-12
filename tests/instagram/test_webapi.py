"""
Test WebAPI.

Test API endpoints.
"""

import pytest
from async_asgi_testclient import TestClient
from fastapi import status

from AppMain.asgi import app

BASE_URL = "/instagram/api"


@pytest.mark.asyncio
async def test_webapi_create_review_invalid() -> None:
    """Create a review."""
    data = {"reviewer_email": "email@example.com", "reviewer_name": "John Doe"}
    async with TestClient(app) as client:
        response = await client.post(f"{BASE_URL}/review/", json=data)

    # Ensure that the request is successful
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.content


@pytest.mark.asyncio
async def test_webapi_create_review() -> None:
    """Create a review."""
    data = {"reviewer_email": "email@review.com", "reviewer_name": "John Doe"}

    async with TestClient(app) as client:
        response = await client.post(f"{BASE_URL}/review/", json=data)

    # Ensure that the request is successful
    assert response.status_code == status.HTTP_201_CREATED, response.content

    # Ensure that the output data matches the input
    response_data = response.json()
    assert response_data["reviewer_email"] == data["reviewer_email"]


@pytest.mark.asyncio
async def test_webapi_list_reviews() -> None:
    """Fetch all reviews."""
    async with TestClient(app) as client:
        response = await client.get(f"{BASE_URL}/review/")

    # Ensure that the request is successful
    assert response.status_code == status.HTTP_200_OK, response.content

    # Ensure that the output data matches the input
    response_data = response.json()

    assert len(response_data) >= 1
