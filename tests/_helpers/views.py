"""
Test Views.

Test web pages.

There is a bug using BaseHTTPMiddleware, Jinja2, and starlette.TestClient
https://github.com/encode/starlette/issues/472

Using async_asgi_testclient.TestClient fix the issue while waiting for an official starlette fix
https://github.com/tiangolo/fastapi/issues/806
"""

from http.cookies import SimpleCookie

import pytest
from async_asgi_testclient import TestClient
from fastapi import status

from sap.settings import IntegrationParams

from AppMain.asgi import app
from AppMain.settings import AppSettings, TestcasesParams
from trellis.xlib.models import BaseMerchantDoc

from .utils import test_params_default, test_params_lydia


def get_page_url(module: str, page_path: str, test_params: TestcasesParams = test_params_default) -> str:
    """Construct URL to access the trellis page."""
    assert test_params
    # return f"/pages/{test_params.beans_card_address}/{module}{page_path}"
    return f"/{module}/pages{page_path}"


@pytest.mark.asyncio
async def _test_view_base(trellis_name: str) -> None:
    """Test redirect from base to home."""
    print(f"=> ({trellis_name=})")

    # Scenario A: Ensure that visitors are directly to the homepage by default
    async with TestClient(app) as client:
        response = await client.get(f"/{trellis_name}/", allow_redirects=False)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"].endswith(f"/{trellis_name}/pages/")


async def _test_views_accessibility(trellis_name: str, jwt_cookie: SimpleCookie, page_name: str) -> None:
    """Test all settings views and ensure they are only accessible when the merchant is authenticated."""
    integration_params: IntegrationParams = getattr(AppSettings, trellis_name.upper())

    # Scenario A: Ensure that non-authenticated merchant are directed to login page
    async with TestClient(app) as client:
        response = await client.get(get_page_url(trellis_name, f"/{page_name}/"), allow_redirects=False)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"].endswith(get_page_url(trellis_name, "/login/"))

    # Scenario B: Test page accessibility when user is authenticated
    async with TestClient(app) as client:
        response = await client.get(
            get_page_url(trellis_name, f"/{page_name}/"), allow_redirects=False, cookies=jwt_cookie
        )
    if integration_params.is_status_available is False and page_name in ["connect"]:
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"].endswith(get_page_url(trellis_name, "/maintenance/"))
    else:
        assert response.status_code == status.HTTP_200_OK, f"Get {response.status_code=}"


@pytest.mark.asyncio
async def _test_view_login(trellis_name: str) -> None:
    """Test Beans oauth."""
    # Scenario A: Ensure that visitors are directly to the homepage by default
    async with TestClient(app) as client:
        response = await client.get(get_page_url(trellis_name, "/login/"), allow_redirects=False)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"].startswith("https://connect.trybeans.com/oauth/authorize/")


@pytest.mark.asyncio
async def _test_view_beans_callback(
    trellis_name: str, merchant_class: type[BaseMerchantDoc], merchant: BaseMerchantDoc | None
) -> None:
    """Ensure that merchants are authenticated and re-directed to the homepage."""
    # Use Lydia's testcases instead of default to ensure that the tests are well sandboxed
    test_params = test_params_lydia

    # Scenario A: A new merchant register (login for the first time)
    await merchant_class.find(merchant_class.beans_card_id == test_params.beans_card_id).delete()
    async with TestClient(app) as client:
        response = await client.get(
            get_page_url(trellis_name, "/beans-callback/", test_params=test_params),
            query_string={"code": test_params.beans_access_token},
            allow_redirects=False,
        )
    cookie_input = response.headers["set-cookie"]
    assert f"trellis_session_{trellis_name}" in cookie_input
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"].endswith(get_page_url(trellis_name, "/", test_params=test_params))

    # Scenario B: An existing merchant login (merchant is already registered in the DB)
    async with TestClient(app) as client:
        response = await client.get(
            get_page_url(trellis_name, "/beans-callback/", test_params=test_params),
            query_string={"code": test_params.beans_access_token},
            allow_redirects=False,
        )
    cookie_input = response.headers["set-cookie"]
    assert f"trellis_session_{trellis_name}" in cookie_input
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"].endswith(get_page_url(trellis_name, "/", test_params=test_params))

    # Scenario C: And existing merchant's access_token has expired or is corrupted
    # Modify the access_token and retry authenticated
    merchant = await merchant_class.find_one(merchant_class.beans_card_id == test_params.beans_card_id)
    assert merchant and merchant.id
    merchant.beans_access_token = ""
    await merchant.save()
    async with TestClient(app) as client:
        response = await client.get(
            get_page_url(trellis_name, "/beans-callback/", test_params=test_params),
            query_string={"code": test_params.beans_access_token},
            allow_redirects=False,
        )
    await merchant.refresh_from_db()
    assert merchant.beans_access_token == test_params.beans_access_token


@pytest.mark.asyncio
async def _test_view_home(trellis_name: str, merchant: BaseMerchantDoc, jwt_cookie: SimpleCookie) -> None:
    """Test homepage."""
    integration_params: IntegrationParams = getattr(AppSettings, trellis_name.upper())

    # Scenario A: Ensure that non-authenticated merchant are directed to login page
    async with TestClient(app) as client:
        response = await client.get(get_page_url(trellis_name, "/"), allow_redirects=False)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"].endswith(get_page_url(trellis_name, "/login/"))

    # Scenario B: Authenticated merchant are redirected to the connect if their integration account is not connected
    async with TestClient(app) as client:
        response = await client.get(get_page_url(trellis_name, "/"), allow_redirects=False, cookies=jwt_cookie)
    if not merchant.get_is_connected():
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"].endswith(get_page_url(trellis_name, "/connect/"))
    elif integration_params.is_status_available is False:
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"].endswith(get_page_url(trellis_name, "/maintenance/"))
    else:
        assert response.status_code == status.HTTP_200_OK
