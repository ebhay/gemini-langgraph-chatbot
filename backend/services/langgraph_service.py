import logging
from typing import TypedDict
from langgraph.graph import StateGraph, END

from services.gemini_service import get_response
from services.tool_service import find_hospitals
from services.scheduler_service import schedule_task
from services.memory_service import get_history, save_conversation

logger = logging.getLogger(__name__)


class ChatState(TypedDict, total=False):
    input: str
    output: str


def chatbot_node(state: ChatState):
    user_input = state.get("input", "").strip()

    if not user_input:
        logger.warning("[NODE] Received empty user input")
        return {"output": "Please enter a message."}

    if "hospital" in user_input.lower():
        try:
            if "in" in user_input.lower():
                location = user_input.lower().split("in")[-1].strip().title()
            else:
                location = "your area"

            hospitals = find_hospitals(location)

            response = f"Here are some hospitals in {location}:\n"
            for h in hospitals:
                response += f"- {h}\n"

            try:
                save_conversation(user_input, response)
            except Exception as e:
                logger.error(f"[NODE] save_conversation() failed (tool): {e}")

            return {"output": response}

        except Exception as e:
            logger.error(f"[TOOL] Hospital lookup failed: {e}")
            return {"output": "Sorry, I couldn't fetch hospital data."}

    if "remind me" in user_input.lower():
        try:
            schedule_task("Reminder completed!", delay=10)

            response = "Reminder set! You will be notified soon."

            try:
                save_conversation(user_input, response)
            except Exception as e:
                logger.error(f"[NODE] save_conversation() failed (scheduler): {e}")

            return {"output": response}

        except Exception as e:
            logger.error(f"[SCHEDULER] Task scheduling failed: {e}")
            return {"output": "Failed to set reminder."}

    try:
        history = get_history(limit=5)
    except Exception as e:
        logger.error(f"[NODE] get_history() failed: {e}")
        history = ""

    prompt = f"""You are a helpful AI assistant. Remember details the user shares about themselves.

Previous conversation:
{history}
User: {user_input}
Assistant:"""

    logger.debug(f"[NODE] Prompt ready (len={len(prompt)} chars)")

    response = get_response(prompt)

    try:
        save_conversation(user_input, response)
    except Exception as e:
        logger.error(f"[NODE] save_conversation() failed: {e}")

    return {"output": response}


graph = StateGraph(ChatState)

graph.add_node("chatbot", chatbot_node)

graph.set_entry_point("chatbot")
graph.add_edge("chatbot", END)

app_graph = graph.compile()
