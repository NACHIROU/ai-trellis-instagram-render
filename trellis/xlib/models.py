"""
Models.

Base models that can be sub-classed independently by each Trellis integration.
"""

import typing
from datetime import datetime

import pydantic

from sap.beanie import Document
from sap.fastapi.user import UserMixin
from sap.pydantic import datetime_utcnow


class BaseMerchantDoc(UserMixin, Document):
    """Base class for all Merchant documents."""

    website: str  # The link to the merchant store
    beans_card_id: str  # The id of the card object on Beans API
    beans_card_address: str  # The uid of the card object on Beans API
    beans_access_token: str | None = None  # Access token used to perform query on Beans API
    beans_authorized: datetime = pydantic.Field(default_factory=datetime_utcnow)  # Last beans_access_token update
    is_active: bool = False  # If the integration is active and connected

    trellis_name: typing.ClassVar[str] = ""

    role: str = "merchant"

    def __repr__(self) -> str:
        """Display a string representation of the object."""
        return f"<{self.__class__.__name__}: {self.beans_card_address}>"

    def __str__(self) -> str:
        """Print object."""
        return self.beans_card_address

    async def get_auth_key(self) -> str:
        """Return an auth_key allowing the user to authenticate. Useful for testing."""
        return self.beans_card_id

    async def refresh_from_db(self) -> None:
        """Reset all attributes using values from database."""
        assert self.id
        new_doc = await self.get(self.id)
        self.__dict__.update(new_doc.__dict__)

    def get_is_connected(self) -> bool:
        """Specify if the merchant has successfully connected to the external app."""
        raise NotImplementedError

    async def disconnect(self) -> None:
        """Disconnect the integration from third party app."""
        raise NotImplementedError

    @classmethod
    async def update_or_create(cls, beans_card_id: str, beans_access_token: str) -> typing.Self:
        """Update a merchant if it is in the database or create a new one if not."""
        return cls(
            beans_card_id=beans_card_id,
            beans_card_address=NotImplemented,
            website=NotImplemented,
            beans_access_token=beans_access_token,
            beans_authorized=datetime.utcnow(),
        )


MerchantT = typing.TypeVar("MerchantT", bound=BaseMerchantDoc)
