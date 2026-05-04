import logging
import time
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

MAX_RETRIES = 3
BACKOFF_BASE = 5  # seconds — doubles each retry: 5s, 10s, 20s


def get_response(prompt: str) -> str:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.debug(f"[GEMINI] Sending prompt (attempt {attempt}, len={len(prompt)} chars)")
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
            error_str = str(e)

            # Rate limit — wait and retry with exponential backoff
            if "429" in error_str or "quota" in error_str.lower():
                wait = BACKOFF_BASE * (2 ** (attempt - 1))  # 5s, 10s, 20s
                logger.warning(
                    f"[GEMINI] Rate limit hit (attempt {attempt}/{MAX_RETRIES}). "
                    f"Waiting {wait}s before retry..."
                )
                if attempt < MAX_RETRIES:
                    time.sleep(wait)
                    continue
                else:
                    logger.error("[GEMINI] All retry attempts exhausted due to rate limiting.")
                    return "The AI service is currently rate-limited. Please wait a moment and try again."

            # Any other error — fail immediately, no retry
            logger.error(f"[GEMINI] Generation failed (non-retryable): {e}")
            return f"Error: {error_str}"

    return "Unexpected error: no response generated."