"""
Fixtures.

Fixtures provides test scenario with baseline data needed to operate.
Learn more: https://docs.pytest.org/en/6.2.x/fixture.html
"""

import typing
from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio

from trellis.instagram.models import MerchantDoc


@pytest.fixture(scope="package", name="trellis_name")
def fixture_trellis_name() -> str:
    """Fixture: name of the trellis integration being tested."""
    return "instagram"


@pytest.fixture(scope="package", name="merchant_class")
def fixture_merchant_class() -> type[MerchantDoc]:
    """Fixture: class of Merchant to use to perform tests."""
    return MerchantDoc


@pytest_asyncio.fixture(scope="package", autouse=True)
async def load_merchant(merchant: MerchantDoc) -> typing.AsyncGenerator[bool, None]:
    """Initialize merchant fixture for testing."""
    await merchant.set(
        {
            "instagram_access_token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "instagram_shop_domain": "test.myshopify.com",
            "doc_meta.created": datetime.now(UTC) - timedelta(days=100),
            "is_active": True,
        }
    )
    yield True
