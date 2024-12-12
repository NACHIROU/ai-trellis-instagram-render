"""
# Crons.

Crons are jobs that run in the background.
The processes that run these jobs are usually referred to as workers.

This is useful for:

- Heavy operations that would take too long to process over an client requests
  but that the client doesn't really have to be waiting for the operation to completed

- It is also useful for repetitive tasks that should on a set schedule.
  For example, you can define a task to run every day at 2pm.

"""

import typing
from datetime import UTC, datetime, timedelta

from beanie.odm.operators.find import logical
from beanie.odm.queries.find import FindMany

from sap.worker.crons import CronStat, FetchStrategy

from trellis.xlib.crons import TrellisCronTask

from .models import MerchantDoc

LATENCY_OLD = 7  # number of days after which a merchant data should re-fetched


class FetchReviewsCron(TrellisCronTask):
    """Fetch reviews for all merchants periodically."""

    def get_queryset(self, *, batch_size: typing.Optional[int] = None, **kwargs: typing.Any) -> FindMany[MerchantDoc]:
        """Use strategy to define the list of merchants to fetch review.

        - new: Fetch review for new merchants
        - old: Fetch review for old merchants
        """
        return MerchantDoc.find_many(
            MerchantDoc.is_active == True,
            logical.Or(
                MerchantDoc.last_review_fetched == None,
                MerchantDoc.last_review_fetched <= datetime.now(UTC) - timedelta(days=LATENCY_OLD),
            ),
            limit=batch_size,
            sort="last_review_fetched",
        )

    async def process(self, *, batch_size: int = 100, **kwargs: typing.Any) -> dict[str, int]:
        """Fetch reviews for merchants using strategy and limiting to batch_size."""
        strategy: FetchStrategy = kwargs["strategy"]
        merchant_list = await self.get_queryset(batch_size=batch_size, strategy=strategy).to_list()
        reviews_processed_count = 0
        merchants_processed_count = 0

        for merchant in merchant_list:
            reviews_processed_count += await fetch_reviews_for_merchant(merchant)
            merchants_processed_count += 1

        return {"reviews_processed": reviews_processed_count, "merchants_processed": merchants_processed_count}

    async def get_stats(self) -> list[CronStat]:
        """Stats.

        merchant_new: count how many new merchants are waiting for review fetching.
        merchant_old: count how many old merchants are waiting for review fetching.
        """
        return [
            CronStat(name="merchants_new", value=await self.get_queryset(strategy=FetchStrategy.NEW).count()),
            CronStat(name="merchants_old", value=await self.get_queryset(strategy=FetchStrategy.OLD).count()),
        ]


async def fetch_reviews_for_merchant(merchant: MerchantDoc) -> int:
    """Fetch all reviews for a merchant."""
    return 0 if merchant else -1
