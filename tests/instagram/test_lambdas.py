import pytest

from trellis.instagram.lambdas import DeleteInstagramReviewLambda
from trellis.instagram.models import MerchantDoc


@pytest.mark.asyncio
async def test_lambda_delete_review(merchant: MerchantDoc) -> None:
    task = DeleteInstagramReviewLambda()
    account_data = {
        "id": "acc_0rq9z8myjwg5rf",
        "first_name": "trellis+acc-codjo@trybeans.com",
        "last_name": "Codjo",
        "email": "trellis+acc-codjo@trybeans.com",
        "birthday": "2000-01-01",
        "beans": 500,
        "beans_value": 5.0,
        "tier_name": "Diamond",
        "tier_expiring": "2030-01-01",
    }

    # test signal packed receive for existing shop
    await task.test_process(merchant.beans_card_id, account_data=account_data)

    # test signal packed receive for non-existing shop
    await task.test_process("0123456789", account_data=account_data)
