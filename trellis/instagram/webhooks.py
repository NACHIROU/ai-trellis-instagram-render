"""
# Webhooks.

The Webhooks endpoint allows the application to receive data from
other applications. Webhooks are event-driven rather than requests-driven.
They typically do not send any data, except from an acknowledgement that
they receive the data that was posted.

They usually do not have a specific authentication, but they should check
the event domain and signature to ensure that the data sent is coming from
the correct source and has not been tempered.

It should accept data formatted as specified by the sender.
https://en.wikipedia.org/wiki/Webhook

To receive webhook on your local machine, use a reverse proxy
https://ngrok.com/
"""

from fastapi import APIRouter, status

from .serializers import CreateReview

router = APIRouter()


@router.post("/review_created/", status_code=status.HTTP_200_OK)
async def review_created(serializer: CreateReview) -> dict[str, str]:
    """
    Receive webhook data.

    Note that event if it is a POST request the webhook always return 200 on success.
    """
    await serializer.create()
    return {"message": "OK"}
