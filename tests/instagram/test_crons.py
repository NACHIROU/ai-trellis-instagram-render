"""
Test Crons.

Test cron jobs.
"""

from datetime import datetime, timedelta

import pytest

from sap.tests.crons import get_filter_queryset_for_merchant
from sap.worker.crons import FetchStrategy

from trellis.instagram.crons import FetchReviewsCron
from trellis.instagram.models import MerchantDoc


@pytest.mark.asyncio
async def test_cron_fetch_reviews(merchant: MerchantDoc, cron_strategy: FetchStrategy) -> None:
    """Test dummy cron to ensure that CronTask base class is functioning."""
    assert merchant.id

    # Reset data before test
    if cron_strategy == FetchStrategy.NEW:
        await merchant.set({"last_review_fetched": None})
    elif cron_strategy == FetchStrategy.OLD:
        await merchant.set({"last_review_fetched": datetime.now() - timedelta(10)})

    # Run cron task
    task = FetchReviewsCron(kwargs={"strategy": cron_strategy, "batch_size": 20})
    response = await task.test_process(
        filter_queryset=get_filter_queryset_for_merchant(model_class=MerchantDoc, merchant_id=merchant.id)
    )
    result = response["result"]

    # Check result
    await merchant.refresh_from_db()
    assert result["reviews_processed"] >= 0
    assert result["merchants_processed"] == 1
