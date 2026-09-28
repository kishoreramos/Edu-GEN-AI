# EduGenie Orchestrator Schemas
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class IntentType(str, Enum):
    """Supported user intent categories."""
    QA = "QA"
    EXPLAIN = "EXPLAIN"
    QUIZ = "QUIZ"
    SUMMARIZE = "SUMMARIZE"
    LEARNING_PATH = "LEARNING_PATH"
    MULTI_ACTION = "MULTI_ACTION"
    CLARIFICATION = "CLARIFICATION"
    UNKNOWN = "UNKNOWN"

class ActionItem(BaseModel):
    """Represents a single step in a multi-action workflow."""
    intent: IntentType
    topic: Optional[str] = None
    input_text: Optional[str] = None
    question_count: Optional[int] = Field(default=3, description="Number of questions if quiz")
    difficulty: Optional[str] = Field(default=None, description="Requested difficulty level")
    depends_on: Optional[str] = Field(
        default=None,
        description="Dependency indicator (e.g. 'previous_result' to consume output of previous step)"
    )

class StructuredIntent(BaseModel):
    """
    Complete structured representation of classified user intent.
    Parsed from Gemini structured output or deterministic analyzer.
    """
    intent: IntentType
    topic: Optional[str] = Field(default=None, description="Extracted educational concept/topic")
    input_text: Optional[str] = Field(default=None, description="Full text or passage if provided")
    difficulty: Optional[str] = Field(default=None, description="BEGINNER, INTERMEDIATE, or ADVANCED")
    question_count: Optional[int] = Field(default=3, description="Number of quiz questions")
    language: str = Field(default="ENGLISH")
    style: Optional[str] = Field(default=None, description="Response style, e.g. SIMPLE, TECHNICAL")
    input_type: str = Field(default="TEXT")
    requires_context: bool = Field(
        default=False,
        description="True if query explicitly relies on conversation context not yet available"
    )
    clarification_prompt: Optional[str] = Field(
        default=None,
        description="Question to ask user if clarification is needed"
    )
    actions: List[ActionItem] = Field(
        default_factory=list,
        description="Sequence of actions if intent is MULTI_ACTION"
    )
    confidence: float = Field(default=1.0)
    reasoning: Optional[str] = Field(default=None, description="Brief rationale for classification")

class ToolResult(BaseModel):
    """Standardized result returned by capability tools to the orchestrator."""
    success: bool
    tool: str
    content: str
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None

class ConversationMessage(BaseModel):
    """Represents a message stored in a session history."""
    role: str = Field(..., description="'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message text content")
    intent: Optional[str] = Field(default=None, description="Classified intent if applicable")
    created_at: Optional[str] = Field(default=None, description="ISO timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class QuizState(BaseModel):
    """Tracks state and performance for an active quiz in a session."""
    quiz_id: str = Field(..., description="Unique quiz identifier")
    topic: str = Field(..., description="Topic of the quiz")
    difficulty: Optional[str] = Field(default=None)
    questions: List[Dict[str, Any]] = Field(default_factory=list)
    score: Optional[int] = Field(default=None, description="User's score if evaluated")
    total: int = Field(default=3, description="Total number of questions")
    user_answers: Dict[str, str] = Field(default_factory=dict)
    weak_areas: List[str] = Field(default_factory=list, description="Identified concepts missed")

class ContextState(BaseModel):
    """Encapsulates active contextual state for multi-turn conversations."""
    current_topic: Optional[str] = Field(default=None, description="Most recent educational topic")
    current_intent: Optional[str] = Field(default=None, description="Most recent intent")
    current_difficulty: Optional[str] = Field(default=None, description="Current difficulty preference")
    last_explanation: Optional[str] = Field(default=None, description="Text of last concept explanation")
    last_summary: Optional[str] = Field(default=None, description="Text of last generated summary")
    last_quiz: Optional[QuizState] = Field(default=None, description="Active or most recent quiz state")
    current_learning_path: Optional[str] = Field(default=None, description="Last generated learning path")
    recent_topics: List[str] = Field(default_factory=list, description="Chronological list of recent topics")

class ChatRequest(BaseModel):
    """Payload for POST /api/chat."""
    message: str = Field(..., min_length=1, description="User's input message")
    session_id: Optional[str] = Field(default=None, description="Optional session id for conversation continuity")

class ChatResponse(BaseModel):
    """Structured response for POST /api/chat."""
    success: bool
    session_id: Optional[str] = Field(default=None, description="Active session ID for follow-up turns")
    intent: str
    reply: str
    data: Dict[str, Any] = Field(default_factory=dict)

