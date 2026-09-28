# EduGenie Q&A Module
import logging

try:
    from .config import generate_gemini_text, is_gemini_configured, GEMINI_KEY_MISSING_ERROR, GEMINI_MODEL
except ImportError:
    from config import generate_gemini_text, is_gemini_configured, GEMINI_KEY_MISSING_ERROR, GEMINI_MODEL

logger = logging.getLogger("EduGenie.QnA")

def answer_question_with_gemini(question: str) -> str:
    """
    Answers general academic and learning questions using Google Gemini.
    Uses centralized GEMINI_MODEL via generate_gemini_text.
    """
    # 1. Input Validation
    if not question or not question.strip():
        return "⚠️ Error: Please provide a valid question."

    # 2. Check Configuration
    if not is_gemini_configured():
        return GEMINI_KEY_MISSING_ERROR

    try:
        prompt = (
            "You are EduGenie, an AI educational tutor. Answer the student's question "
            "clearly, accurately, and concisely in simple terms suitable for learners:\n\n"
            f"Question: {question.strip()}"
        )
        return generate_gemini_text(prompt)
    except Exception as e:
        logger.error(f"Error answering question: {e}", exc_info=True)
        return f"⚠️ Error in QnA: {str(e)}"
