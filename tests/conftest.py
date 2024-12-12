"""
Fixtures.

Fixtures provides test scenario with baseline data needed to operate.
Learn more: https://docs.pytest.org/en/6.2.x/fixture.html
"""

import asyncio
import typing
from http.cookies import SimpleCookie

import pytest
import pytest_asyncio
from fastapi import Request, Response

from sap.rest import BeansClient
from sap.worker.crons import FetchStrategy

from AppMain.asgi import document_models, initialize_beanie
from AppMain.settings import AppSettings
from trellis.xlib.auth import TrellisJWTAuth
from trellis.xlib.models import BaseMerchantDoc

from ._helpers.utils import test_params_default


@pytest.fixture(scope="session")
def event_loop() -> typing.Generator[asyncio.events.AbstractEventLoop, None, None]:
    """Force pytest fixtures to use async loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialise_db() -> typing.AsyncGenerator[bool, None]:
    """Initialize DB connection for all tests."""
    print("Connecting to MongoDB")
    print("Initializing Beanie")

    # Use a special database for testing
    AppSettings.MONGO.db = "trellis_test"

    await initialize_beanie()

    # Clear all collections
    for doc_model in document_models:
        await doc_model.find_all().delete()

    yield True  # suspended until tests are done

    print("Disconnecting from MongoDB")


@pytest_asyncio.fixture(scope="session", name="cron_strategy", params=list(FetchStrategy))
async def fixture_cron_strategy(request: pytest.FixtureRequest) -> FetchStrategy:
    """Fixture: Return the different fetching strategies used by cron tasks."""
    strategy: FetchStrategy = request.param
    return strategy


@pytest_asyncio.fixture(scope="package", name="merchant")
async def fixture_merchant(merchant_class: type[BaseMerchantDoc]) -> typing.AsyncGenerator[BaseMerchantDoc, None]:
    """Fixture: a merchant object."""

    merchant = await merchant_class.find_one(merchant_class.beans_card_id == test_params_default.beans_card_id)

    if not merchant:
        client = BeansClient(access_token=test_params_default.beans_access_token)
        card = await client.get("ultimate/card/current")
        merchant = await merchant_class(
            beans_card_id=test_params_default.beans_card_id,
            beans_access_token=test_params_default.beans_access_token,
            beans_card_address=card["address"],
            website=card["website"],
            is_active=True,
        ).create()

    yield merchant

    await merchant.disconnect()


@pytest_asyncio.fixture(scope="package", name="jwt_cookie")
async def fixture_jwt_cookie(merchant: BaseMerchantDoc) -> SimpleCookie:
    """Fixture: cookie of an authenticated merchant."""
    response = Response()
    request_scope = {
        "type": "http",
        "http_version": "1.1",
        "server": ("127.0.0.1", 8000),
        "client": ("127.0.0.1", 59957),
        "scheme": "https",
        "method": "GET",
        "headers": [("host", "localhost:8000")],
        "path_params": {"card_address": test_params_default.beans_card_address[1::]},
    }
    request = Request(scope=request_scope)
    jwt_auth = TrellisJWTAuth(user_model=type(merchant))
    await jwt_auth.login(response, request=request, user=merchant)
    cookie_input = response.headers["set-cookie"]
    cookie_data: SimpleCookie = SimpleCookie(input=cookie_input)
    return cookie_data
