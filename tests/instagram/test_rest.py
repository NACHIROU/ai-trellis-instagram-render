"""
Test Rest Client.

Test That the Rest Client is well setup
"""

import pytest

from sap.rest.rest_exceptions import Rest401Error

from trellis.instagram.rest import InstagramClient


@pytest.mark.asyncio
async def test_instagram_rest_client() -> None:
    """Test that the REST wrapper for Instagram API is functional."""
    client = InstagramClient("wrong-api-token")

    with pytest.raises(Rest401Error):
        await client.get("shops/info")
