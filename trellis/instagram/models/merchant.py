"""
# Models: Merchant.

The Merchant model represents an online store.
This model contains all parameters that are specific
to an online store.
"""

import typing
from datetime import datetime

import pymongo

from trellis.xlib.models import BaseMerchantDoc


class MerchantDoc(BaseMerchantDoc):
    """Merchant object."""

    instagram_shop_domain: str = ""  # Shop domain associate to the connected Instagram account
    instagram_username: typing.Optional[str] = None  # username associate to the connected Instagram account
    instagram_id: typing.Optional[str] = None  # id associate to the connected Instagram account
    instagram_access_token: typing.Optional[str] = None  # Access token used to perform query on Instagram API
    instagram_authorized: typing.Optional[datetime] = None  # Last access_token update
    last_review_fetched: typing.Optional[datetime] = None

    trellis_name: typing.ClassVar[str] = "instagram"

    def get_is_connected(self) -> bool:
        """Specify if the merchant has successfully connected their Instagram account."""
        return self.instagram_access_token is not None

    async def disconnect(self) -> None:
        """Disconnect the integration from Instagram."""
        await self.set({"instagram_access_token": None, "is_active": False})

    class Settings:
        """Settings for the database collection."""

        name = "instagram_merchant"
        indexes = [
            pymongo.IndexModel("beans_card_id", unique=True),
        ]
