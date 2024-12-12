"""
Auth.

Authenticate the user before they access secure views.
"""

import typing

from fastapi import Request

from sap.beanie.exceptions import Object404Error
from sap.fastapi.auth import JWTAuth

from .models import BaseMerchantDoc


class TrellisJWTAuth(JWTAuth):
    """
    Custom JWT Auth.

    Each trellis should be authenticated independently.
    Auth cookie and auth URL is unique per trellis.
    """

    user_model: type[BaseMerchantDoc]
    auth_cookie_expires: typing.ClassVar[int] = 60 * 60 * 6  # expiration = 6 hours

    def get_auth_login_url(self, request: Request) -> str:
        """Retrieve the login url where user are redirect in case of auth failure."""
        return f"/{self.user_model.trellis_name}/pages/login/"

    def get_auth_cookie_key(self, request: Request) -> str:
        """Retrieve key used to define the authentication cookie."""
        # card_address = request.path_params.get("card_address", "xxx")
        card_address = "xxx"
        return f"trellis_session_{self.user_model.trellis_name}__${card_address}"

    async def find_user(self, jwt_token: str) -> BaseMerchantDoc:
        """Ensure the authenticated user is active."""
        merchant: BaseMerchantDoc = await super().find_user(jwt_token=jwt_token)
        try:
            assert merchant.beans_access_token
        except AssertionError as exc:
            raise Object404Error("Could not find user with valid beans access token.") from exc
        return merchant
