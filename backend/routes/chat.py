from fastapi import APIRouter
from pydantic import BaseModel
from services.langgraph_service import app_graph

router = APIRouter()

class ChatRequest(BaseModel):
    user_input: str

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        result = app_graph.invoke({"input": request.user_input})
    except Exception as e:
        print("[ERROR] invoke failed:", e)
        return {"response": f"Error: {str(e)}"}

    output = result.get("output") if result else None

    if not output:
        return {"response": "I couldn't generate a response. Please try again."}

    return {"response": output}