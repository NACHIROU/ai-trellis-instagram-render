"""
Application Settings.

The settings file contains all the configuration of the application.
Use this file to configure any parameters that should be set server-side.

Settings can be adjusted depending on the environment the app is running on.
The environment is usually defined by the `APP_ENV` OS environment variable that
can be set on the local machine or on the server.

!!! warning !!!
For security reason, do not put in this file any secret key.
Add them as OS environment variables or put them in the `.env` file.

https://github.com/theskumar/python-dotenv

"""

import logging
import logging.config
import os
import pathlib
import typing

import pydantic
import pydantic_settings
from fastapi.templating import Jinja2Templates

from sap.settings import DatabaseParams, IntegrationParams


class TestcasesParams(pydantic.BaseModel):
    """
    Parameters to for testcases.

    This params are only used to automate testcases.
    """

    beans_card_id: str = ""
    beans_card_address: str = ""
    beans_access_token: str = ""
    beans_member_1_id: str = ""
    beans_member_1_email: str = ""


class _Settings(pydantic_settings.BaseSettings):
    """
    Application Settings.

    The setting are load from environment variables:
    https://pydantic-docs.helpmanual.io/usage/settings/

    All env variable should be prefixed with APP_SETTINGS_
    For example to set the LOG_DIR, use: APP_SETTINGS_LOG_DIR="/tmp/"
    """

    model_config = pydantic_settings.SettingsConfigDict(
        extra="ignore",
        env_file=os.getenv("APP_DOTENV", ".env"),
        env_file_encoding="utf-8",
        env_prefix="APP_SETTINGS_",
        env_nested_delimiter="__",
    )

    PROJ_NAME: str = "trellis"

    # Envs
    APP_ENV: str = os.getenv("APP_ENV", "DEV")
    LOG_DIR: str = "/tmp/"
    APP_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent
    THEME_COFFEE_CDN: str = "https://theme-coffee-staging.vercel.app"

    # Databases
    MONGO: DatabaseParams

    # Tokens
    TESTCASES: TestcasesParams = TestcasesParams()
    CRYPTO_SECRET: str  # a key used for encryption
    AIRTABLE_TOKEN: str = ""
    BEANS_OAUTH_URL: str = (
        "https://connect.trybeans.com/oauth/authorize/?"
        "client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    )

    # SSL, used on localhost
    SSL_KEYFILE: str | None = None
    SSL_CERTFILE: str | None = None

    TRELLIS_LIST: list[str] = ["instagram"]

    # Instagram
    INSTAGRAM: IntegrationParams

    @property
    def is_prod(self) -> bool:
        """Return True if production environment."""
        return self.APP_ENV == "PROD"


AppSettings = _Settings()


# ###################################
# #     Logging       ###############
# ###################################


def logging_setter() -> dict[str, typing.Any]:
    """Set the logging config for all apps in `AppSettings.TRELLIS_LIST`."""
    log_dir: str = AppSettings.LOG_DIR
    app_names: list[str] = AppSettings.TRELLIS_LIST
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "level": "WARNING",
            "handlers": ["file_trellis"],
        },
        "formatters": {
            "verbose": {"format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"},
            "simple": {"format": "%(asctime)s %(levelname)s %(message)s"},
        },
        "handlers": {
            "null": {
                "level": "DEBUG",
                "class": "logging.NullHandler",
            },
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
            "file_trellis": {
                "level": "DEBUG",
                "class": "logging.FileHandler",
                "filename": os.path.join(log_dir, "trellis.log"),
                "formatter": "simple",
            },
            "file_celery": {
                "level": "DEBUG",
                "class": "logging.FileHandler",
                "filename": os.path.join(log_dir, "celery.log"),
                "formatter": "simple",
            },
            "file_sap": {
                "level": "DEBUG",
                "class": "logging.FileHandler",
                "filename": os.path.join(log_dir, "sap.log"),
                "formatter": "simple",
            },
            **{
                f"file_trellis_{app_name}": {
                    "level": "DEBUG",
                    "class": "logging.FileHandler",
                    "filename": os.path.join(log_dir, f"trellis_{app_name}.log"),
                    "formatter": "simple",
                }
                for app_name in app_names
            },
        },
        "loggers": {
            "trellis": {
                "level": "DEBUG",
                "handlers": ["console", "file_trellis"],
                "propagate": False,
            },
            **{
                f"trellis.{app_name}": {
                    "level": "DEBUG",
                    "handlers": ["console", f"file_trellis_{app_name}"],
                    "propagate": False,
                }
                for app_name in app_names
            },
            "sap": {
                "level": "WARN",
                "handlers": ["console", "file_sap"],
                "propagate": False,
            },
            "celery.task": {
                "level": "WARN",
                "handlers": ["console", "file_celery"],
                "propagate": False,
            },
            "celery.worker": {
                "level": "WARN",
                "handlers": ["console", "file_celery"],
                "propagate": False,
            },
        },
    }


logging.config.dictConfig(logging_setter())

logger = logging.getLogger("trellis")


# ###################################
# #     Logging       ###############
# ###################################

templates = Jinja2Templates(directory=AppSettings.APP_DIR / "templates")
