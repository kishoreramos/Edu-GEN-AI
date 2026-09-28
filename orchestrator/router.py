# EduGenie Tool Router with Context Tracking
import re
import uuid
import logging
from typing import Optional, Dict, Any, List

from .schemas import (
    IntentType,
    StructuredIntent,
    ToolResult,
    ChatResponse,
    ContextState,
    QuizState
)
from .session_manager import default_session_manager

try:
    from ..qna import answer_question_with_gemini
    from ..explanation_module import explain_topic
    from ..summary_module import summarize_text
    from ..quiz_module import generate_quiz
    from ..learning_path import get_learning_recommendations
except ImportError:
    from qna import answer_question_with_gemini
    from explanation_module import explain_topic
    from summary_module import summarize_text
    from quiz_module import generate_quiz
    from learning_path import get_learning_recommendations

logger = logging.getLogger("EduGenie.Router")

GREETING_REPLY = (
    "Hello! I am EduGenie, your personal AI learning assistant. "
    "I can help you with:\n"
    "• Asking academic questions (Q&A)\n"
    "• Explaining difficult concepts in simple terms\n"
    "• Testing your knowledge with interactive quizzes\n"
    "• Summarizing educational passages\n"
    "• Generating structured learning roadmaps\n\n"
    "What would you like to learn today?"
)

UNKNOWN_HELP_REPLY = (
    "I'm not sure how to assist with that request. EduGenie is an educational assistant "
    "specialized in concept explanations, Q&A, quizzes, text summarization, and learning roadmaps. "
    "Try asking: 'Explain recursion simply', 'Test me on photosynthesis', or 'Give me a roadmap to learn SQL'."
)

def route_intent(
    intent: StructuredIntent,
    raw_message: str,
    context: Optional[ContextState] = None
) -> ToolResult:
    """
    Dispatches the structured intent to the appropriate existing EduGenie module.
    Maintains and updates contextual state (topic, last quiz, explanation).
    """
    logger.info(f"Routing intent: {intent.intent} (Topic: {intent.topic})")
    msg_lower = raw_message.lower().strip()

    # 1. QA Intent
    if intent.intent == IntentType.QA:
        target_question = intent.topic or raw_message
        answer = answer_question_with_gemini(target_question)
        if context and intent.topic:
            context.current_topic = intent.topic
            _append_recent_topic(context, intent.topic)
        return ToolResult(
            success=True,
            tool="QA",
            content=answer,
            data={"answer": answer, "question": target_question}
        )

    # 2. Concept Explanation Intent
    elif intent.intent == IntentType.EXPLAIN:
        target_topic = intent.topic or (context.current_topic if context else raw_message)
        explanation = explain_topic(target_topic)
        if context:
            context.current_topic = target_topic
            context.last_explanation = explanation
            _append_recent_topic(context, target_topic)
        return ToolResult(
            success=True,
            tool="EXPLAIN",
            content=explanation,
            data={"topic": target_topic, "explanation": explanation}
        )

    # 3. Quiz Generation Intent & Quiz Performance Feedback
    elif intent.intent == IntentType.QUIZ:
        # Check if user is reporting quiz score (e.g. "I got 2 wrong")
        score_match = re.search(r"\b(?:i\s+got|missed)\s+(\d+)\s+(?:wrong|incorrect)\b", msg_lower)
        if score_match or msg_lower in ["i got 2 wrong", "i got 1 wrong", "i got 0 wrong"]:
            wrong_count = int(score_match.group(1)) if score_match else 2
            total = context.last_quiz.total if (context and context.last_quiz) else 3
            quiz_topic = context.last_quiz.topic if (context and context.last_quiz) else (context.current_topic if context else "the quiz")
            score = max(0, total - wrong_count)

            if context and context.last_quiz:
                context.last_quiz.score = score

            reply = (
                f"Good effort on the '{quiz_topic}' quiz! You scored {score} out of {total}. "
                "Practice makes progress! Would you like me to explain the concepts you found challenging, "
                "or generate a new quiz to try again?"
            )
            return ToolResult(
                success=True,
                tool="QUIZ",
                content=reply,
                data={
                    "quiz_feedback": True,
                    "score": score,
                    "total": total,
                    "topic": quiz_topic
                }
            )

        # Standard Quiz Generation
        target_content = intent.input_text or intent.topic or (context.current_topic if context else raw_message)
        quiz = generate_quiz(target_content)
        question_count = len(quiz) if isinstance(quiz, list) else 0
        topic_name = intent.topic or (context.current_topic if context else "your topic")

        if context:
            context.current_topic = topic_name
            context.last_quiz = QuizState(
                quiz_id=uuid.uuid4().hex[:8],
                topic=topic_name,
                questions=quiz if isinstance(quiz, list) else [],
                total=question_count
            )
            _append_recent_topic(context, topic_name)

        reply_header = f"Here is a practice quiz on '{topic_name}' ({question_count} questions):"
        return ToolResult(
            success=True,
            tool="QUIZ",
            content=reply_header,
            data={"quiz": quiz, "topic": topic_name}
        )

    # 4. Text Summarization Intent
    elif intent.intent == IntentType.SUMMARIZE:
        target_text = intent.input_text or intent.topic or raw_message
        summary = summarize_text(target_text)
        if context:
            context.last_summary = summary
        return ToolResult(
            success=True,
            tool="SUMMARIZE",
            content=summary,
            data={"summary": summary}
        )

    # 5. Learning Path Intent
    elif intent.intent == IntentType.LEARNING_PATH:
        target_topic = intent.topic or (context.current_topic if context else raw_message)
        recommendation = get_learning_recommendations(target_topic)
        if context:
            context.current_learning_path = recommendation
            if intent.topic:
                context.current_topic = intent.topic
                _append_recent_topic(context, intent.topic)
        return ToolResult(
            success=True,
            tool="LEARNING_PATH",
            content=recommendation,
            data={"topic": target_topic, "recommendation": recommendation}
        )

    # 6. Multi-Action Workflow
    elif intent.intent == IntentType.MULTI_ACTION:
        from .workflow import execute_multi_action_workflow
        result = execute_multi_action_workflow(intent, raw_message)
        if context and intent.topic:
            context.current_topic = intent.topic
            _append_recent_topic(context, intent.topic)
        return result

    # 7. Clarification Intent
    elif intent.intent == IntentType.CLARIFICATION:
        clarification_msg = intent.clarification_prompt or (
            f"Could you please clarify what you would like to do with '{intent.topic or 'this topic'}'? "
            "You can ask for an explanation, take a quiz, summarize text, or request a learning roadmap."
        )
        return ToolResult(
            success=True,
            tool="CLARIFICATION",
            content=clarification_msg,
            data={"clarification": clarification_msg, "requires_context": intent.requires_context}
        )

    # 8. Unknown / Conversational
    else:
        is_greeting = any(msg_lower.startswith(g) for g in ["hello", "hi", "hey", "greetings", "good morning"])
        reply = GREETING_REPLY if is_greeting else UNKNOWN_HELP_REPLY
        return ToolResult(
            success=True,
            tool="UNKNOWN",
            content=reply,
            data={"is_greeting": is_greeting}
        )

def _append_recent_topic(context: ContextState, topic: str):
    """Adds topic to recent_topics maintaining max 5 unique entries."""
    if not topic:
        return
    clean_t = topic.strip()
    if clean_t in context.recent_topics:
        context.recent_topics.remove(clean_t)
    context.recent_topics.append(clean_t)
    if len(context.recent_topics) > 5:
        context.recent_topics = context.recent_topics[-5:]

def process_message(
    message: str,
    session_id: Optional[str] = None,
    session_manager=None
) -> ChatResponse:
    """
    Complete stateful orchestration pipeline with performance instrumentation:
    1. Retrieve or initialize persistent session state (SQLite).
    2. Retrieve bounded conversation history.
    3. Record user message in session history.
    4. Fast local pre-routing / intent classification.
    5. Route intent and update learning state.
    6. Record assistant reply in session history.
    7. Persist updated context state to SQLite.
    8. Return standardized ChatResponse with latency instrumentation.
    """
    import time
    t_start = time.time()

    sm = session_manager or default_session_manager
    from .intent_classifier import classify_intent

    # 1. Retrieve or create session
    active_session_id, context = sm.get_or_create_session(session_id)

    # 2. Get bounded recent conversation history (max 10 messages = 5 turns)
    recent_history = sm.get_recent_messages(active_session_id, limit=10)

    # 3. Add incoming user message to session history
    sm.add_message(active_session_id, role="user", content=message)

    # 4. Classify intent with contextual awareness (measured)
    t_intent_start = time.time()
    intent = classify_intent(message, context=context, recent_history=recent_history)
    t_intent_end = time.time()

    # 5. Route intent to appropriate tool (measured)
    t_route_start = time.time()
    result = route_intent(intent, message, context=context)
    t_route_end = time.time()

    t_total = time.time() - t_start
    total_ms = round(t_total * 1000, 1)
    intent_ms = round((t_intent_end - t_intent_start) * 1000, 1)
    module_ms = round((t_route_end - t_route_start) * 1000, 1)

    # Attach timing metadata
    data_dict = result.data.copy() if result.data else {}
    data_dict["timings"] = {
        "total_ms": total_ms,
        "intent_ms": intent_ms,
        "module_ms": module_ms
    }

    logger.info(
        f"⏱️ [PERF] Total: {total_ms}ms | Intent ({intent.intent}): {intent_ms}ms | Module ({result.tool}): {module_ms}ms"
    )

    # 6. Save assistant reply to session history
    sm.add_message(
        active_session_id,
        role="assistant",
        content=result.content,
        intent=result.tool,
        metadata=data_dict
    )

    # 7. Persist updated context state to SQLite
    sm.update_session_context(active_session_id, context)

    # 8. Return standardized ChatResponse
    return ChatResponse(
        success=result.success,
        session_id=active_session_id,
        intent=result.tool,
        reply=result.content,
        data=data_dict
    )
