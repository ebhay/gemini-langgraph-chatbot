from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from services.gemini_service import get_response
from services.memory_service import get_history, save_conversation

# Define state schema properly using TypedDict
# This is required in modern LangGraph so it knows which keys to track
class ChatState(TypedDict, total=False):
    input: str
    output: str

# Node function with memory
def chatbot_node(state: ChatState):
    user_input = state.get("input", "")

    # Fetch past conversations (short-term memory)
    try:
        history = get_history()
    except Exception as e:
        print("[DEBUG] get_history() FAILED:", e)
        history = ""

    # Build prompt with memory
    prompt = f"""You are a helpful AI assistant. Remember details the user shares about themselves.

Previous conversation:
{history}

User: {user_input}
Assistant:"""

    # Get AI response
    response = get_response(prompt)

    # Save current conversation (long-term memory)
    try:
        save_conversation(user_input, response)
    except Exception as e:
        print("[DEBUG] save_conversation() FAILED:", e)

    return {"output": response}


# Build graph
graph = StateGraph(ChatState)

graph.add_node("chatbot", chatbot_node)

graph.set_entry_point("chatbot")
graph.add_edge("chatbot", END)   # ✅ correct modern API, replaces set_finish_point

# Compile graph
app_graph = graph.compile()