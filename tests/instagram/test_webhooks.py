"""
Test Webhooks.

Test webhooks endpoints.
"""

import pytest
from async_asgi_testclient import TestClient
from fastapi import status

from AppMain.asgi import app

BASE_URL = "/instagram/hooks"


@pytest.mark.asyncio
async def test_hooks_review_created() -> None:
    """Test webhook on review created."""
    data = {"reviewer_email": "email@review.com", "reviewer_name": "John Doe"}

    async with TestClient(app) as client:
        response = await client.post(f"{BASE_URL}/review_created/", json=data)

    # Ensure that the request is successful
    assert response.status_code == status.HTTP_200_OK, response.content

    # Ensure that the output data matches the input
    response_data = response.json()
    assert response_data["message"] == "OK"
