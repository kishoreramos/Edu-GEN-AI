# EduGenie - FastAPI Application
import os
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Query, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

# Flexible imports to support both package and direct module execution
try:
    from .qna import answer_question_with_gemini
    from .explanation_module import explain_topic
    from .summary_module import summarize_text
    from .quiz_module import generate_quiz
    from .learning_path import get_learning_recommendations
    from .config import is_gemini_configured
except ImportError:
    from qna import answer_question_with_gemini
    from explanation_module import explain_topic
    from summary_module import summarize_text
    from quiz_module import generate_quiz
    from learning_path import get_learning_recommendations
    from config import is_gemini_configured

try:
    from .orchestrator.router import process_message
    from .orchestrator.schemas import ChatRequest, ChatResponse
    from .orchestrator.session_manager import default_session_manager
except ImportError:
    from orchestrator.router import process_message
    from orchestrator.schemas import ChatRequest, ChatResponse
    from orchestrator.session_manager import default_session_manager

logger = logging.getLogger("EduGenie.App")

# Base directory resolution
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="EduGenie",
    description="Google Gemini Powered AI Learning Assistant",
    version="1.0.0"
)

# Mount static assets and template engine
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Pydantic Schemas for type safety and validation
class TopicRequest(BaseModel):
    topic: str = Field(..., min_length=1, description="The topic to explain or recommend")

class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, description="The text or topic for summarization/quiz")

# -----------------------------------------------------------------------------
# Web UI Entrypoint
# -----------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    """Serves the baseline multi-feature educational web interface."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"gemini_configured": is_gemini_configured()}
    )

# -----------------------------------------------------------------------------
# 1. Q&A Endpoint (POST & GET /qa)
# -----------------------------------------------------------------------------
@app.api_route("/qa", methods=["GET", "POST"])
async def answer_question(request: Request, question: Optional[str] = Query(None, description="Student question")):
    """
    Answers an educational question using Gemini.
    Documented routes: POST /qa, GET /qa?question=...
    """
    q = question
    if request.method == "POST":
        try:
            data = await request.json()
            if isinstance(data, dict):
                q = data.get("question") or data.get("text") or q
        except Exception:
            pass

    if not q or not str(q).strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Please provide a valid question."}
        )
    answer = answer_question_with_gemini(str(q).strip())
    return {"question": str(q).strip(), "answer": answer}

# -----------------------------------------------------------------------------
# 2. Explanation Endpoint (POST /explain)
# -----------------------------------------------------------------------------
@app.post("/explain")
async def explain_api(request: Request):
    """
    Explains a concept in simple terms for learners.
    Supports both Pydantic-style JSON and direct request.json() extraction.
    Documented route: POST /explain
    """
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Invalid JSON payload."}
        )

    topic = (data.get("topic") or data.get("text")) if isinstance(data, dict) else None
    if not topic or not str(topic).strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Please provide a topic."}
        )

    explanation = explain_topic(str(topic).strip())
    return {"topic": topic, "explanation": explanation}

# -----------------------------------------------------------------------------
# 3. Summarization Endpoint (POST /summarize)
# -----------------------------------------------------------------------------
@app.post("/summarize")
async def summarize_api(request: Request):
    """
    Summarizes long educational content into clear, concise takeaways.
    Documented route: POST /summarize
    """
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Invalid JSON payload."}
        )

    text = data.get("text") if isinstance(data, dict) else None
    if not text or not str(text).strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Please provide text to summarize."}
        )

    summary = summarize_text(str(text).strip())
    return {"summary": summary}

# -----------------------------------------------------------------------------
# 4. Quiz Generation Endpoint (POST /quiz)
# -----------------------------------------------------------------------------
@app.post("/quiz")
async def quiz_api(request: Request):
    """
    Generates 3 MCQs with options and correct answers from a text/topic.
    Documented route: POST /quiz
    """
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Invalid JSON payload."}
        )

    text = (data.get("text") or data.get("topic")) if isinstance(data, dict) else None
    if not text or not str(text).strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Please provide text for quiz."}
        )

    quiz = generate_quiz(str(text).strip())
    logger.info(f"Generated {len(quiz)} quiz questions.")
    return JSONResponse(content={"quiz": quiz})

# -----------------------------------------------------------------------------
# 5. Learning Path Recommendations Endpoint (POST & GET /learn/recommendations)
# -----------------------------------------------------------------------------
@app.api_route("/learn/recommendations", methods=["GET", "POST"])
async def learning_recommendation_api(request: Request, topic: Optional[str] = Query(None, description="Topic to learn")):
    """
    Generates a personalized, structured learning roadmap.
    Documented routes: POST /learn/recommendations, GET /learn/recommendations?topic=...
    """
    t = topic
    if request.method == "POST":
        try:
            data = await request.json()
            if isinstance(data, dict):
                t = data.get("topic") or data.get("text") or t
        except Exception:
            pass

    if not t or not str(t).strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Please provide a topic."}
        )

    clean_topic = str(t).strip()
    recommendation = get_learning_recommendations(clean_topic)
    return {"topic": clean_topic, "recommendation": recommendation, "recommendations": recommendation}

# -----------------------------------------------------------------------------
# 6. Conversational Orchestration Endpoint (POST /api/chat)
# -----------------------------------------------------------------------------
@app.post("/api/chat", response_model=ChatResponse)
async def chat_api(request: ChatRequest):
    """
    Intelligent conversational endpoint:
    Accepts natural language user messages, understands intent,
    routes to appropriate existing EduGenie capabilities, and returns
    structured response data.
    """
    if not request.message or not request.message.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "error": "Message cannot be empty."}
        )

    response = process_message(request.message, session_id=request.session_id)
    return response

# -----------------------------------------------------------------------------
# 7. Session Endpoints (POST /api/session, GET /api/session/{session_id}/history)
# -----------------------------------------------------------------------------
@app.post("/api/session")
async def create_session_api():
    """Explicitly initializes a new conversation session."""
    session_id = default_session_manager.create_session()
    return {"success": True, "session_id": session_id}

@app.get("/api/session/{session_id}/history")
async def get_session_history_api(session_id: str, limit: int = 10):
    """Retrieves recent conversation history for a given session."""
    history = default_session_manager.get_recent_messages(session_id, limit=limit)
    return {"session_id": session_id, "messages": [m.model_dump() for m in history]}

@app.get("/api/sessions")
async def get_all_sessions_api(limit: int = 20):
    """Retrieves recent conversation sessions for sidebar navigation."""
    sessions = default_session_manager.get_all_sessions(limit=limit)
    return {"sessions": sessions}


