"""
# Routes.

The `router` list routes URLS to any accessible endpoint for a sub-app.
The router in routes.py is referred as the main router for this sub-app.

There are 3 types of routes that usually cover all useful cases:
    - API
    - Webhooks
    - Views
"""

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from .views import router as router_pages
from .webapi import router as router_api
from .webhooks import router as router_webhooks

router = APIRouter()

router.include_router(router_pages, prefix="/pages", tags=["instagram", "pages"])
router.include_router(router_api, prefix="/api", tags=["instagram", "api"])
router.include_router(router_webhooks, prefix="/hooks", tags=["instagram", "webhooks"])


@router.get("/")
async def root(request: Request) -> RedirectResponse:
    """Redirect to the homepage."""
    return RedirectResponse(request.url_for("instagram:home"))
