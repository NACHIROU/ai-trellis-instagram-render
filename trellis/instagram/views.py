"""
# Views.

The Views endpoint displays a web interface that users
can use to browse the application. These endpoints use Cookies based
authentication when it is needed to authenticate the user.

The views renders the HTML files located in the templates folder.
The templating engine used is Jinja2:
https://jinja.palletsprojects.com/

It should accept Forms and returns an HTML response.
https://en.wikipedia.org/wiki/Web_page
https://en.wikipedia.org/wiki/Form_(HTML)
"""

import typing
import urllib.parse
from datetime import datetime

import oauthlib.oauth2.rfc6749.errors
import pyfacebook
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, Response

from sap.fastapi import Flash, FlashLevel
from sap.rest import BeansClient

from AppMain.settings import AppSettings, logger, templates
from trellis.xlib.auth import TrellisJWTAuth

from .models import MerchantDoc, ReviewDoc
from .serializers import CreateReview, RetrieveReview

router = APIRouter()
jwt_auth = TrellisJWTAuth(user_model=MerchantDoc)
DependsMerchant = typing.Annotated[MerchantDoc, Depends(jwt_auth.authenticate)]


@router.get("/example/")
async def example_page(request: Request) -> Response:
    """Display the app example page."""
    reviews = await ReviewDoc.find_all().to_list()
    return templates.TemplateResponse(
        "example.jinja",
        context={
            "reviews": RetrieveReview.from_list(reviews),
            "request": request,
            "form": {},
        },
    )


@router.post("/example/")
async def example_page_post(request: Request) -> Response:
    """Display the app example page."""
    form_data = await request.form()
    serializer = CreateReview(**form_data)
    await serializer.create()
    reviews = await ReviewDoc.find_all().to_list()
    return templates.TemplateResponse(
        "example.jinja",
        context={
            "reviews": RetrieveReview.from_list(reviews),
            "request": request,
            "form": serializer,
        },
    )


@router.get("/")
async def home(request: Request, merchant: DependsMerchant) -> Response:
    """Homepage and main navigation."""
    if not merchant.get_is_connected():
        return RedirectResponse(request.url_for("instagram:connect"))
    return templates.TemplateResponse(
        "instagram/home.jinja",
        context={
            "request": request,
            "merchant": merchant,
        },
    )


@router.get("/connect/")
async def connect(request: Request, merchant: DependsMerchant) -> Response:
    """Prompt the merchant connect the integration's account."""
    params = {
        "client_id": AppSettings.INSTAGRAM.third_party_public,
        "redirect_uri": request.url_for("instagram:instagram_callback"),
        "response_type": "code",
        "scope": "business_basic, business_content_publish, business_manage_comments, business_manage_messages",
        "state": pyfacebook.GraphAPI.STATE,
    }
    redirect_url = "https://www.instagram.com/oauth/authorize/?" + urllib.parse.urlencode(params)
    return templates.TemplateResponse(
        "instagram/connect.jinja",
        context={
            "request": request,
            "merchant": merchant,
            "redirect_url": redirect_url,
        },
    )


@router.get("/status/")
async def status(request: Request, merchant: DependsMerchant) -> Response:
    """When the account is already connected."""
    return templates.TemplateResponse(
        "instagram/status.jinja",
        context={
            "request": request,
            "merchant": merchant,
        },
    )


@router.get("/credentials/")
async def credentials(request: Request, merchant: DependsMerchant) -> Response:
    """Force the merchant to authenticate through Instagram."""
    return templates.TemplateResponse(
        "instagram/credentials.jinja",
        context={
            "request": request,
            "merchant": merchant,
        },
    )


@router.get("/logs/")
async def logs(request: Request, merchant: DependsMerchant) -> Response:
    """List of merchant."""
    return templates.TemplateResponse(
        "instagram/logs.jinja",
        context={
            "request": request,
            "merchant": merchant,
        },
    )


@router.get("/rules/")
async def rules(request: Request, merchant: DependsMerchant) -> Response:
    """When the merchant want activate the rules."""
    return templates.TemplateResponse(
        "instagram/rules.jinja",
        context={
            "request": request,
            "merchant": merchant,
        },
    )


@router.get("/login/")
async def login(request: Request) -> Response:
    """Force the merchant to authenticate through Beans oAuth."""
    return RedirectResponse(
        AppSettings.BEANS_OAUTH_URL.format(
            client_id=AppSettings.INSTAGRAM.beans_public,
            redirect_uri=request.url_for("instagram:beans_callback"),
        )
    )


@router.get("/beans-callback/")
async def beans_callback(request: Request, code: str) -> Response:
    """Exchange oauth code to retrieve access token and identify the merchant."""

    integration_key = await BeansClient.get_access_token(
        code=code,
        beans_public=AppSettings.INSTAGRAM.beans_public,
        beans_secret=AppSettings.INSTAGRAM.beans_secret,
    )
    merchant = await MerchantDoc.find_one(MerchantDoc.beans_card_id == integration_key["card"])
    if not merchant:
        client = BeansClient(access_token=integration_key["secret"])
        card = await client.get("ultimate/card/current")

        merchant = await MerchantDoc(
            beans_card_id=integration_key["card"],
            beans_access_token=integration_key["secret"],
            beans_card_address=card["address"],
            website=card["website"],
            is_active=True,
        ).create()

    else:
        merchant.beans_access_token = integration_key["secret"]
        await merchant.save()

    response = RedirectResponse(request.url_for("instagram:home"))
    await jwt_auth.login(response=response, request=request, user=merchant)

    return response


@router.get("/instagram-callback/")
async def instagram_callback(request: Request, merchant: DependsMerchant) -> Response:
    """Exchange oauth code to retrieve access token and identify the merchant."""
    # A- Exchange code with access token
    api = pyfacebook.GraphAPI(
        app_id=AppSettings.INSTAGRAM.third_party_public,
        app_secret=AppSettings.INSTAGRAM.third_party_secret,
        oauth_flow=True,
    )
    try:
        api.exchange_user_access_token(
            response=str(request.url),
            redirect_uri=request.url_for("instagram:instagram_callback"),
        )
    except oauthlib.oauth2.rfc6749.errors.MismatchingStateError as exc:
        logger.exception("Unable to connect to instagram account: %s", str(exc))

        Flash.add_message(request, f"Unable to connect to instagram account: {str(exc)}", level=FlashLevel.ERROR)
        return RedirectResponse(request.url_for("instagram:connect"))

    # B- Extend access token validity
    token_data = api.exchange_long_lived_user_access_token()
    api.access_token = token_data["access_token"]

    # C- Retrieve Instagram user information
    info = api.get_object("me", fields="id,username")

    # D- Save info to database
    merchant.instagram_id = info["id"]
    merchant.instagram_username = info["username"]
    merchant.instagram_access_token = token_data["access_token"]
    merchant.instagram_authorized = datetime.utcnow()
    await merchant.save()
    return RedirectResponse(request.url_for("instagram:home"))
