"""
Tasks.

Background tasks that run a worker server.
These tasks can run even while the user is not online,
not making any active HTTP requests, or not using the application.
"""

from typing import Any, ClassVar, Optional

from sap.worker.crons import CronResponse, CronStat, CronStorage, CronTask, TestStorage

from AppMain.asgi import initialize_beanie


class TrellisCronTask(CronTask):
    """Subclass CronTask. Run results and stats are store on airtable."""

    storage_class: ClassVar[type[CronStorage]] = TestStorage

    def get_queryset(self, *, batch_size: Optional[int] = None, **kwargs: Any) -> Any:
        """Fetch the list of elements to process."""
        raise NotImplementedError

    async def handle_process(self, *args: Any, **kwargs: Any) -> CronResponse:
        """Initialize Beanie and run the task."""
        await initialize_beanie()
        return await super().handle_process(*args, **kwargs)

    async def process(self, *, batch_size: int = 100, **kwargs: Any) -> Any:
        """Run the cron task and process elements."""
        raise NotImplementedError

    async def get_stats(self) -> list[CronStat]:
        """Give stats about the number of elements left to process."""
        raise NotImplementedError
