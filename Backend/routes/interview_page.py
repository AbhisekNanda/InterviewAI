import os
from fastapi import APIRouter
from fastapi.responses import FileResponse

page_router = APIRouter()

# Get the absolute path to the 'static' directory
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")

@page_router.get("/interview/{interview_id}", response_class=FileResponse)
async def get_interview_page(interview_id: int):
    """
    This endpoint serves the interview.html file. The JavaScript inside
    the file will get the interview_id from the URL.
    """
    return os.path.join(static_dir, "interview.html")