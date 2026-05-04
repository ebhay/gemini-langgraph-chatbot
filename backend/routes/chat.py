from fastapi import APIRouter
from services.gemini_service import get_response

router = APIRouter()

@router.post("/chat")
async def chat(user_input: str):
    response = get_response(user_input)
    return {"response": response}