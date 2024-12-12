"""
# Models: Review.

Beanie is a python ODM (Object Document Mapper) for MongoDB which
relies on pydantic for validation and motor for async DB operations.

https://roman-right.github.io/beanie/
https://pydantic-docs.helpmanual.io/
https://motor.readthedocs.io/
"""

import beanie
import pydantic
import pymongo

from sap.beanie.document import Document

from .merchant import MerchantDoc


class ReviewDoc(Document):
    """Review object."""

    merchant: beanie.Link[MerchantDoc]
    reviewer_email: pydantic.EmailStr
    reviewer_name: str
    resource_id: int

    def __str__(self) -> str:
        """Display a string representation of the object."""
        return f"{self.merchant}: {self.reviewer_email}"

    class Settings:
        """Settings for the database collection."""

        name = "instagram_review"
        indexes = [
            pymongo.IndexModel("resource_id", unique=True),
        ]
