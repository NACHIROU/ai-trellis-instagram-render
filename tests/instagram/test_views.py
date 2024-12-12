"""
Test Views.

Test web pages.

There is a bug using BaseHTTPMiddleware, Jinja2, and starlette.TestClient
https://github.com/encode/starlette/issues/472

Using async_asgi_testclient.TestClient fix the issue while waiting for an official starlette fix
https://github.com/tiangolo/fastapi/issues/806
"""

import typing
from http.cookies import SimpleCookie
from unittest import mock

import pyfacebook
import pytest
from async_asgi_testclient import TestClient
from fastapi import status

from AppMain.asgi import app
from tests._helpers.utils import test_params_default
from tests._helpers.views import (
    _test_view_base,
    _test_view_beans_callback,
    _test_view_home,
    _test_view_login,
    _test_views_accessibility,
)
from trellis.instagram.models import MerchantDoc

from .samples import instagram_tokens

test_view_base = _test_view_base
test_view_home = _test_view_home
test_view_login = _test_view_login
test_view_beans_callback = _test_view_beans_callback


@pytest.mark.asyncio
async def test_view_example(trellis_name: str) -> None:
    """Test example page."""
    async with TestClient(app) as client:
        response = await client.get(f"/{trellis_name}/pages/example/")
    assert response.status_code == status.HTTP_200_OK

    data = {"reviewer_email": "form-view@review.com", "reviewer_name": "Form View"}
    async with TestClient(app) as client:
        response = await client.post(f"/{trellis_name}/pages/example/", form=data)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize("page_name", ["connect", "rules", "logs", "status", "credentials"])
@pytest.mark.asyncio
async def test_views_accessibility(trellis_name: str, jwt_cookie: SimpleCookie, page_name: str) -> None:
    """Accessibility test to ensure that the views are working."""
    await _test_views_accessibility(trellis_name=trellis_name, jwt_cookie=jwt_cookie, page_name=page_name)


@pytest.mark.asyncio
async def test_view_beans_callback_register(
    trellis_name: str, merchant_class: type[MerchantDoc], merchant: typing.Optional[MerchantDoc]
) -> None:
    """Test authenticating the merchant when first login."""

    # A. Ensure that merchants are authenticated and re-directed to the homepage

    merchant = await merchant_class.find_one(
        merchant_class.beans_access_token == test_params_default.beans_access_token
    )
    # if merchant:
    #     await merchant.delete()

    async with TestClient(app) as client:
        response = await client.get(
            f"/{trellis_name}/pages/beans-callback/",
            query_string={"code": test_params_default.beans_access_token},
            allow_redirects=False,
        )
    cookie_input = response.headers["set-cookie"]
    assert f"trellis_session_{trellis_name}" in cookie_input
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"].endswith(f"/{trellis_name}/pages/")


@pytest.mark.parametrize(
    ("code", "state", "is_auth_success"),
    [
        ("", "", False),
        ("CODE_WRONG", "STATE_WRONG", False),
        ("CODE_WRONG", "STATE_GOOD", False),
        ("CODE_GOOD", "STATE_WRONG", False),
        ("CODE_GOOD", "STATE_GOOD", True),
    ],
)
@pytest.mark.asyncio
async def test_view_instagram_callback(
    jwt_cookie: SimpleCookie,
    merchant: MerchantDoc,
    code: str,
    state: str,
    is_auth_success: bool,
) -> None:
    """Test that the user oauth code is correctly exchange for the access_token"""

    await merchant.set(
        {
            "instagram_id": None,
            "instagram_username": None,
            "instagram_access_token": None,
            "instagram_authorized": None,
        },
    )

    # Fetch cookies to instantiate session in order to create the verifier
    async with TestClient(app) as client:
        response = await client.get("instagram/pages/connect", cookies=jwt_cookie)
    jwt_cookie.load(response.cookies)

    # Verify code
    if code:
        instagram_tokens["oauth_callback_params"]["code"] = code
    else:
        instagram_tokens["oauth_callback_params"].pop("code")

    # Verify state
    if state:
        instagram_tokens["oauth_callback_params"]["state"] = state
    else:
        instagram_tokens["oauth_callback_params"].pop("state")

    # Create mock that fakes successfully access_token exchange
    original__exchange_access_token = pyfacebook.IGBasicDisplayApi.exchange_user_access_token
    original__exchange_long_lived_access_token = pyfacebook.IGBasicDisplayApi.exchange_long_lived_user_access_token

    def mock__exchange_user_access_token(
        self: pyfacebook.IGBasicDisplayApi,
        response: str,
        redirect_uri: str,
        **kwargs: None,
    ) -> dict[str, typing.Any]:
        if code == "CODE_GOOD" and state == "STATE_GOOD":
            self.access_token = instagram_tokens["oauth_object"]["access_token"]
            return {"access_token": instagram_tokens["oauth_object"]["access_token"]}
        result: dict[str, typing.Any] = original__exchange_access_token(self, response, redirect_uri, **kwargs)
        return result

    def mock__exchange_long_lived_access_token(
        self: pyfacebook.IGBasicDisplayApi, access_token: typing.Optional[str] = None
    ) -> dict[str, typing.Any]:
        access_token = access_token or self.access_token
        if access_token == instagram_tokens["oauth_object"]["access_token"]:
            return {
                "access_token": instagram_tokens["oauth_object_long_live"]["access_token"],
                "user_id": instagram_tokens["sample_instagram_user"]["id"],
            }
        result: dict[str, typing.Any] = original__exchange_long_lived_access_token(self, access_token)
        return result

    # Perform the callback test
    with (
        mock.patch.object(
            pyfacebook.IGBasicDisplayApi,
            "exchange_user_access_token",
            side_effect=mock__exchange_user_access_token,
            autospec=True,
        ),
        mock.patch.object(
            pyfacebook.IGBasicDisplayApi,
            "exchange_long_lived_user_access_token",
            side_effect=mock__exchange_long_lived_access_token,
            autospec=True,
        ),
    ):
        async with TestClient(app) as client:
            response = await client.get(
                "/instagram/pages/instagram-callback/",
                query_string=instagram_tokens["oauth_callback_params"],
                allow_redirects=False,
                cookies=jwt_cookie,
            )

    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT

    # Ensure that when the callback is successful, all instagram attributes has been set for the merchant
    if is_auth_success:
        assert response.headers["location"].endswith("/instagram/pages/")
        await merchant.refresh_from_db()
        assert merchant.instagram_access_token is not None
        assert merchant.instagram_username is not None
        assert merchant.instagram_id is not None
    else:
        assert response.headers["location"].endswith("/instagram/pages/connect/")
        await merchant.refresh_from_db()
        assert merchant.instagram_access_token is None
        assert merchant.instagram_authorized is None
        assert merchant.instagram_id is None
        assert merchant.instagram_username is None
        assert merchant.get_is_connected() is False
