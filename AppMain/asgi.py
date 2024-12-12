"""
ASGI.

This is MAIN entrypoint to the application.
It exposes the ASGI callable as a module-level variable named ``app``.

"""

import logging
import typing
from contextlib import asynccontextmanager
from importlib import import_module

import beanie
from fastapi import APIRouter, FastAPI, Request, Response, status
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from sap.beanie.client import BeanieClient
from sap.fastapi import Flash
from sap.fastapi.middleware import InitBeanieMiddleware, LogServerErrorMiddleware

from .settings import AppSettings, logger, templates


@asynccontextmanager
async def lifespan(current_app: FastAPI) -> typing.AsyncGenerator[None, None]:
    """Initialize beanie on startup."""
    assert current_app
    await initialize_beanie()
    # await update_uvicorn_logger()
    yield


# Initialize application
app = FastAPI(docs_url=None, redoc_url=None, routes=[])
# Bugs with using starlette path when using Mount
# curl http://localhost:8000/tokenify/pages/login/
# expected path=/tokenify/pages/login/
# output path=/pages/login/
# https://github.com/encode/starlette/issues/1336

# Mount static folder
app.routes.append(Mount(path="/static", app=StaticFiles(directory=AppSettings.APP_DIR / "static"), name="static"))

# Load sub-apps routes and documents
document_models: list[typing.Type[beanie.Document]] = []
for trellis_name in AppSettings.TRELLIS_LIST:
    models_module = import_module(f"trellis.{trellis_name}.models")
    routes_module = import_module(f"trellis.{trellis_name}.routes")

    # initialize router with default routes for each trellis
    router: APIRouter = getattr(routes_module, "router")

    # Mount sub-apps routes
    app.routes.append(Mount(path=f"/{trellis_name}", app=router, name=trellis_name))

    # Retrieve the lists of documents for beanie initialization
    for model_name in models_module.__all__:
        document_models.append(getattr(models_module, model_name))


# Register middleware
app.add_middleware(InitBeanieMiddleware, mongo_params=AppSettings.MONGO, document_models=document_models)
app.add_middleware(SessionMiddleware, session_cookie="starlette", secret_key=AppSettings.CRYPTO_SECRET, max_age=None)
if AppSettings.APP_ENV != "PROD":
    app.add_middleware(LogServerErrorMiddleware)

# Templates
templates.env.globals["get_flashed_messages"] = Flash.get_messages
templates.env.globals["AppSettings"] = AppSettings


# Events to run on startups
async def initialize_beanie() -> None:
    """Initialize beanie on startup."""
    await BeanieClient.init(mongo_params=AppSettings.MONGO, document_models=document_models)


# Always log exception
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Log all request validation errors to a file."""
    logger.exception(exc.errors())
    return await request_validation_exception_handler(request=request, exc=exc)


async def update_uvicorn_logger() -> None:
    """Log all uvicorn errors."""
    logger_uvicorn = logging.getLogger("uvicorn.access")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger_uvicorn.addHandler(handler)


@app.get("/health/", status_code=status.HTTP_200_OK)
async def health() -> dict[str, str]:
    """Health check."""
    return {"message": "OK"}


@app.get("/", status_code=status.HTTP_200_OK)
async def index(request: Request) -> Response:
    """Home page."""
    return templates.TemplateResponse("index.jinja", {"request": request})
