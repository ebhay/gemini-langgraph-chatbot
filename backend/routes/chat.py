import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from services.langgraph_service import app_graph

router = APIRouter()

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    user_input: str

    @field_validator("user_input")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("user_input cannot be empty or whitespace")
        return v.strip()


@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        result = app_graph.invoke({"input": request.user_input})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ROUTE] Graph invocation failed: {e}")
        return {"response": f"Error: {str(e)}"}

    output = result.get("output") if result else None

    if not output or not output.strip():
        logger.warning("[ROUTE] Graph returned empty output")
        return {"response": "I couldn't generate a response. Please try again."}

    return {"response": output}