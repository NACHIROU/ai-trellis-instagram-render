"""
# WebAPI.

The API endpoint  is queried by other applications
to communicate with this application. This endpoint usually relies
on a header based authenticated encoded in the request headers.
Commonly Basic or Bearer Auth.

It should accept and returns data formatted in JSON.

The API is structured with  Representational state transfer architecture:
https://en.wikipedia.org/wiki/Representational_state_transfer
"""

from fastapi import APIRouter, status

from .models import ReviewDoc
from .serializers import CreateReview, RetrieveReview

router = APIRouter()


@router.get("/review/", status_code=status.HTTP_200_OK)
async def api_list_reviews() -> list[RetrieveReview]:
    """Return a list of reviews in the DB."""
    review_list = await ReviewDoc.find_all().to_list()
    return RetrieveReview.from_list(review_list)


@router.post("/review/", status_code=status.HTTP_201_CREATED)
async def api_create_review(serializer: CreateReview) -> RetrieveReview:
    """Create a review and insert in the DB."""
    review: ReviewDoc = await serializer.create()
    return RetrieveReview(review)
