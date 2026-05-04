from typing import TypedDict
from langgraph.graph import StateGraph, END

from services.gemini_service import get_response
from services.tool_service import find_hospitals
from services.scheduler_service import schedule_task
from services.memory_service import get_history, save_conversation


# State schema
class ChatState(TypedDict, total=False):
    input: str
    output: str


# Node function with tool + memory + background tasks
def chatbot_node(state: ChatState):
    user_input = state.get("input", "").strip()

    # 🔹 TOOL ROUTING (FIRST PRIORITY)
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

            return {"output": response}

        except Exception as e:
            print("[DEBUG] Tool failed:", e)
            return {"output": "Sorry, I couldn't fetch hospital data."}


    # 🔹 BACKGROUND TASK TRIGGER (NEW)
    if "remind me" in user_input.lower():
        try:
            schedule_task("Reminder completed!", delay=10)
            return {"output": "Reminder set! You will be notified soon."}
        except Exception as e:
            print("[DEBUG] Scheduler failed:", e)
            return {"output": "Failed to set reminder."}


    # 🔹 MEMORY + GEMINI FLOW
    try:
        history = get_history()
    except Exception as e:
        print("[DEBUG] get_history() FAILED:", e)
        history = ""

    prompt = f"""You are a helpful AI assistant. Remember details the user shares about themselves.

Previous conversation:
{history}

User: {user_input}
Assistant:"""

    # 🔹 Call Gemini
    response = get_response(prompt)

    # 🔹 Save conversation
    try:
        save_conversation(user_input, response)
    except Exception as e:
        print("[DEBUG] save_conversation() FAILED:", e)

    return {"output": response}


# Build graph
graph = StateGraph(ChatState)

graph.add_node("chatbot", chatbot_node)

graph.set_entry_point("chatbot")
graph.add_edge("chatbot", END)

# Compile
app_graph = graph.compile()