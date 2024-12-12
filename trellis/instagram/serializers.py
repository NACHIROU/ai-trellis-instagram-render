"""
# Serializers.

Handle data validation.
"""

import random
import typing
from dataclasses import dataclass

import pydantic

from .models import ReviewDoc


@dataclass
class RetrieveReview:
    """Serialize an object."""

    id: str
    reviewer_email: pydantic.EmailStr
    reviewer_name: str

    def __init__(self, instance: ReviewDoc) -> None:
        """Serialize a single object instance."""
        self.id = str(instance.id)
        self.reviewer_email = instance.reviewer_email
        self.reviewer_name = instance.reviewer_name

    @classmethod
    def from_list(cls, data_list: list[ReviewDoc]) -> list[typing.Self]:
        """Serialize a list of objects."""
        return [cls(x) for x in data_list]


class CreateReview(pydantic.BaseModel):
    """Handle validation operations."""

    reviewer_email: pydantic.EmailStr
    reviewer_name: str

    @pydantic.validator("reviewer_email")
    @classmethod
    def validate_reviewer_email(cls, value: str) -> str:
        """Check whether the provided data is correct."""
        if value.endswith("@example.com"):
            raise ValueError("example.com emails are not allowed")
        return value

    async def create(self) -> ReviewDoc:
        """Insert the object in the DB."""
        review = ReviewDoc(
            reviewer_email=self.reviewer_email,
            reviewer_name=self.reviewer_name,
            resource_id=random.randint(0, 1000),
            merchant=None,
        )
        return await review.create()
