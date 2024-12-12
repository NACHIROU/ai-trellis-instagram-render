"""
Utils.

Re-usable methods and functions for all test cases.
"""

import copy
import typing

from sap.rest import BeansClient, rest_exceptions

from AppMain.settings import AppSettings, TestcasesParams

test_params_default = AppSettings.TESTCASES
test_params_lydia = TestcasesParams(
    beans_card_id="card_0rltefob",
    beans_card_address="$lydiashop",
    beans_access_token="sk_0m1oc67o79dhyszvcx6g830y247vbwqq28792",
)


async def setup_beans_rule(rule_uid: str, is_installed: bool) -> dict[str, typing.Any] | None:
    """Set up a rule as fixture."""
    client = BeansClient(access_token=test_params_default.beans_access_token)

    if is_installed:
        return await client.post("liana/rule/", json={"uid": rule_uid})

    try:
        await client.delete(f"liana/rule/{rule_uid}")
    except rest_exceptions.Rest404Error:
        pass

    return None


class SampleOAuthTokens(typing.TypedDict, total=True):
    """Define a standard for oauth sample tokens."""

    oauth_callback_params: dict[str, typing.Any]
    oauth_object: dict[str, typing.Any]
    extra: dict[str, typing.Any]


def get_test_parameters_oauth(
    tokens: SampleOAuthTokens,
) -> tuple[tuple[str, str, str], list[tuple[bool, dict[str, str], bool]]]:
    """Generate parameters to run oauth testcases scenario."""

    params_names = ("is_merchant_authorized", "callback_params", "is_auth_success")

    callback_params_good: dict[str, str] = tokens["oauth_callback_params"]
    callback_params_wrong: dict[str, str] = copy.copy(callback_params_good)
    for x in callback_params_wrong:
        callback_params_wrong[x] = (
            "invalidoauthcallbackparameter"  # generate_random_string(len(callback_params_good[x]))
        )

    params_values: list[tuple[bool, dict[str, str], bool]] = [
        # A. No oauth callback params => redirect to connect with error message
        (False, {}, False),
        # B. Bad oauth callback params => redirect to connect with error message
        (False, callback_params_wrong, False),
        # C. Good oauth callback params, New merchant => install and redirect to home
        (False, callback_params_good, True),
        # D. Good oauth callback params, Existing merchant reinstall => install and redirect to home
        (True, callback_params_good, True),
    ]

    return params_names, params_values
