from fastapi import APIRouter
from .. import schemas

router = APIRouter(prefix="/bot", tags=["bot"])


@router.post("/greeting", response_model=schemas.BotGreetingResponse)
def get_bot_greeting(request: schemas.BotGreetingRequest):
    """
    Generate a greeting message for a bot meeting record.
    """
    greeting_message = f"Hello, I am {request.bot_name} and I will be recording this meeting about {request.meeting_topic}"
    return {"greeting": greeting_message}
