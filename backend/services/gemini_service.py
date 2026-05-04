import logging
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)

model = genai.GenerativeModel(model_name)

logger.info(f"[GEMINI] Initialized model: {model_name}")


def get_response(prompt: str) -> str:
    try:
        logger.debug(f"[GEMINI] Sending prompt (len={len(prompt)} chars)")
        response = model.generate_content(prompt)

        if response.candidates:
            text = response.candidates[0].content.parts[0].text
            if not text or not text.strip():
                logger.warning("[GEMINI] Model returned empty text in candidate")
                return "I received an empty response. Please try again."
            return text
        else:
            logger.warning("[GEMINI] No candidates returned by model")
            return "No response from model"

    except Exception as e:
        logger.error(f"[GEMINI] Generation failed: {e}")
        return f"Error: {str(e)}"