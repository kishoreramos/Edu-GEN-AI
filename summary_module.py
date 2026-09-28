# Summary Module - EduGenie
import logging

try:
    from .config import generate_gemini_text, is_gemini_configured, GEMINI_KEY_MISSING_ERROR, GEMINI_MODEL
except ImportError:
    from config import generate_gemini_text, is_gemini_configured, GEMINI_KEY_MISSING_ERROR, GEMINI_MODEL

logger = logging.getLogger("EduGenie.Summary")

def summarize_text(text: str) -> str:
    """
    Summarizes educational text into clear, concise, and easy-to-understand key points.
    Uses centralized GEMINI_MODEL via generate_gemini_text.
    """
    if not text or not text.strip():
        return "⚠️ Error: Please provide text to summarize."

    if not is_gemini_configured():
        return GEMINI_KEY_MISSING_ERROR

    try:
        prompt = (
            "Summarize the following educational text in simple, concise language. "
            "Highlight the most crucial concepts and definitions while avoiding unnecessary repetition:\n\n"
            f"{text.strip()}"
        )
        return generate_gemini_text(prompt)
    except Exception as e:
        logger.error(f"Error summarizing text: {e}", exc_info=True)
        return f"⚠️ Error in Summary: {str(e)}"
