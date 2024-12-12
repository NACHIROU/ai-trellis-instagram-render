"""
Rest.

Rest client for instagram API.
"""

import httpx

from sap.rest import RestClient


class InstagramClient(RestClient):
    """Async Instagram API Client.

    An async wrapper around the Instagram API.
    Common errors are handled by the wrapper.
    """

    base_url: str = "https://graph.facebook.com/v18.0/"
    access_token: str
    scopes: list[str] = ["read_shops", "read_reviewers", "read_reviews", "read_settings"]

    def __init__(self, access_token: str) -> None:
        """Initialize the API client."""
        super().__init__()
        self.access_token = access_token

    def _get_client(self) -> httpx.AsyncClient:
        headers = {"Authorization": f"Bearer {self.access_token}"}
        return httpx.AsyncClient(headers=headers)
