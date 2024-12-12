"""
# Models.

Beanie is a python ODM (Object Document Mapper) for MongoDB which
relies on pydantic for validation and motor for async DB operations.

https://roman-right.github.io/beanie/
https://pydantic-docs.helpmanual.io/
https://motor.readthedocs.io/
"""

from .merchant import MerchantDoc
from .review import ReviewDoc

__all__ = [
    "MerchantDoc",
    "ReviewDoc",
]
