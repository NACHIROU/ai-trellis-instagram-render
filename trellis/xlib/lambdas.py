"""
Lambdas refers to async background tasks.

They run code in response to events which are typically messages sent to a queue.
"""

import typing

from sap.worker import LambdaResponse, LambdaTask, SignalPacket

from AppMain.asgi import initialize_beanie

from .models import MerchantT


class TrellisLambdaTask(LambdaTask, typing.Generic[MerchantT]):
    """Subclass LambdaTask in other to automate Merchant authentication."""

    merchant_model: typing.Type[MerchantT]
    packet: SignalPacket

    async def handle_process(self, *args: str, **kwargs: typing.Any) -> LambdaResponse:
        """Authenticate the merchant associated to the identifier and run the lambda task."""
        await initialize_beanie()
        identifier: str = args[0]
        model = self.merchant_model
        merchant: MerchantT | None = await model.find_one(model.beans_card_id == identifier, model.is_active == True)
        if not merchant:
            return LambdaResponse(result=False, error=f"MERCHANT_NOT_FOUND {identifier}")
        result: LambdaResponse = await self.process(merchant=merchant, **kwargs)
        return result

    async def process(self, merchant: MerchantT, **kwargs: typing.Any) -> LambdaResponse:
        """Run the lambda task."""
        raise NotImplementedError
