"""
lambdas.

Lambdas are background tasks that run remotely on a worker.
"""

import typing

from sap.worker import SignalPacket

from trellis.instagram.models import MerchantDoc, ReviewDoc
from trellis.xlib.lambdas import TrellisLambdaTask


class DeleteInstagramReviewLambda(TrellisLambdaTask[MerchantDoc]):
    """Delete reviews data when the loyalty program membership is cancelled."""

    packet = SignalPacket("stem.liana.*.account.delete", providing_args=["identifier", "account_data"])
    merchant_model = MerchantDoc

    async def process(self, merchant: MerchantDoc, **kwargs: typing.Any) -> typing.Any:
        """Delete review data associated to member account."""
        account_data = kwargs["account_data"]
        await ReviewDoc.find(
            ReviewDoc.merchant == merchant.id, ReviewDoc.reviewer_email == account_data["email"]
        ).delete()
        return True
