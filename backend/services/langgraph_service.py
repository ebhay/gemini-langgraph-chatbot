import logging
import json
from typing import TypedDict
from langgraph.graph import StateGraph, END
from services.gemini_service import get_response
from services.tool_service import find_hospitals
from services.scheduler_service import schedule_task
from services.memory_service import get_history, save_conversation
from services.profile_service import get_user_profile, update_user_profile

logger = logging.getLogger(__name__)

class ChatState(TypedDict, total=False):
    input: str
    output: str
    session_id: str
    user_id: int

def tool_node(state: ChatState):
    user_input = state.get("input", "")
    session_id = state.get("session_id", "default")
    user_id = state.get("user_id")
    try:
        location = "your area"
        if "in" in user_input.lower():
            location = user_input.lower().split("in")[-1].strip().title()
        hospitals = find_hospitals(location)
        response = f"Here are some hospitals in {location}:\n" + "\n".join([f"- {h}" for h in hospitals])
        save_conversation(user_id, user_input, response, session_id=session_id)
        return {"output": response}
    except Exception as e:
        logger.error(f"[TOOL] Hospital lookup failed: {e}")
        return {"output": "Sorry, I couldn't fetch hospital data."}

def scheduler_node(state: ChatState):
    user_input = state.get("input", "")
    session_id = state.get("session_id", "default")
    user_id = state.get("user_id")
    try:
        reminder_text = "Reminder: Your task is complete!"
        if "remind me to" in user_input.lower():
            reminder_text = "Reminder: " + user_input.lower().split("remind me to")[-1].strip()
        elif "remind me about" in user_input.lower():
            reminder_text = "Reminder: " + user_input.lower().split("remind me about")[-1].strip()
        schedule_task(user_id, reminder_text, delay=10)
        response = f"I've scheduled that for you. You'll get a notification in 10 seconds: \"{reminder_text}\""
        save_conversation(user_id, user_input, response, session_id=session_id)
        return {"output": response}
    except Exception as e:
        logger.error(f"[SCHEDULER] Task failed: {e}")
        return {"output": "Failed to set reminder."}

def chat_node(state: ChatState):
    user_input = state.get("input", "").strip()
    session_id = state.get("session_id", "default")
    user_id = state.get("user_id")
    if not user_input:
        return {"output": "Please enter a message."}
    history = get_history(user_id, session_id=session_id)
    profile = get_user_profile(user_id)
    profile_str = "\n".join([f"- {k}: {v}" for k, v in profile.items()]) if profile else "No details known yet."
    prompt = f"""You are a highly capable AI assistant with long-term memory.
--- USER CONTEXT ---
LONG-TERM FACTS KNOWN ABOUT USER:
{profile_str}
SHORT-TERM CONVERSATION HISTORY:
{history}
---
USER INPUT: {user_input}
SYSTEM INSTRUCTIONS:
1. Use the facts known about the user to personalize your response.
2. If the user mentions a new personal fact (name, age, city, hobby, preference), you MUST acknowledge it naturally in your reply.
3. CRITICAL: If you learn a new fact, you MUST append a machine-readable block at the VERY END of your response in this EXACT format:
   [EXTRACT: {{"key": "value"}}]
   Example: If they say "I am 20", add [EXTRACT: {{"age": "20"}}] at the end.
4. Keep your conversational response friendly and concise.
Assistant:"""
    response = get_response(prompt)
    clean_response = response
    if "[EXTRACT:" in response:
        try:
            parts = response.split("[EXTRACT:")
            clean_response = parts[0].strip()
            fact_json = parts[1].split("]")[0].strip()
            fact_data = json.loads(fact_json)
            for k, v in fact_data.items():
                update_user_profile(user_id, k, str(v))
                logger.info(f"[PROFILE] Extracted fact: {k}={v}")
        except Exception as e:
            logger.error(f"[PROFILE] Extraction failed: {e}")
    save_conversation(user_id, user_input, clean_response, session_id=session_id)
    return {"output": clean_response}

def router_node(state: ChatState):
    return state

def route_decision(state: ChatState) -> str:
    user_input = state.get("input", "").lower()
    if "hospital" in user_input:
        return "tool"
    if "remind me" in user_input:
        return "scheduler"
    return "chat"

graph = StateGraph(ChatState)
graph.add_node("router", router_node)
graph.add_node("chat", chat_node)
graph.add_node("tool", tool_node)
graph.add_node("scheduler", scheduler_node)
graph.set_entry_point("router")
graph.add_conditional_edges("router", route_decision, {"chat": "chat", "tool": "tool", "scheduler": "scheduler"})
graph.add_edge("chat", END)
graph.add_edge("tool", END)
graph.add_edge("scheduler", END)
app_graph = graph.compile()
