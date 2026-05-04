import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("API key not found")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-3-flash-preview")

def get_response(prompt):
    try:
        response = model.generate_content(prompt)

        # 🔥 CORRECT WAY
        if response.candidates:
            return response.candidates[0].content.parts[0].text
        else:
            return "No response from model"

    except Exception as e:
        print("ERROR:", e)
        return f"Error: {str(e)}"