# Learning Path Module - EduGenie
import logging

try:
    from .config import generate_gemini_text, is_gemini_configured, GEMINI_KEY_MISSING_ERROR, GEMINI_MODEL
except ImportError:
    from config import generate_gemini_text, is_gemini_configured, GEMINI_KEY_MISSING_ERROR, GEMINI_MODEL

logger = logging.getLogger("EduGenie.LearningPath")

def get_learning_recommendations(topic: str) -> str:
    """
    Generates a personalized, structured learning roadmap from beginner to advanced levels
    for a given topic, including estimated timelines and recommended resources.
    Uses centralized GEMINI_MODEL via generate_gemini_text.
    """
    if not topic or not topic.strip():
        return "⚠️ Error: Please provide a topic for learning recommendations."

    if not is_gemini_configured():
        return GEMINI_KEY_MISSING_ERROR

    prompt = f"""You are an expert AI tutor.
The student wants to learn about: {topic.strip()}.
Suggest a structured, adaptive, and comprehensive learning path organized as follows:

1. Overview: Brief roadmap introduction
2. Beginner Level: Core foundational concepts, estimated study time (e.g. 1-2 weeks), and key topics
3. Intermediate Level: Practical application, deeper topics, hands-on exercises, estimated time
4. Advanced Level: Mastery topics, real-world project ideas, optimization, estimated time
5. Recommended Resources: High-quality books, official documentation, videos, and interactive practice platforms
6. Adaptive Study Tips: Advice on how to approach studying this subject effectively

Format your response clearly with Markdown headings and bullet points for high readability.
"""

    try:
        res = generate_gemini_text(prompt)
        logger.info(f"Gemini response received for topic '{topic.strip()}'.")
        return res
    except Exception as e:
        logger.error(f"Error generating learning recommendations: {e}")
        return f"⚠️ Error occurred while generating learning recommendations: {str(e)}"
