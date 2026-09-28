# EduGenie Intent Classifier with Context Resolution
import re
import json
import logging
from typing import Optional, List, Dict, Any

from .schemas import IntentType, StructuredIntent, ActionItem, ContextState, ConversationMessage
try:
    from ..config import generate_gemini_text, is_gemini_configured
except ImportError:
    from config import generate_gemini_text, is_gemini_configured

logger = logging.getLogger("EduGenie.IntentClassifier")

SYSTEM_CLASSIFIER_PROMPT = """You are the Intent Classification Engine for EduGenie, an AI educational assistant.
Analyze the user's message in the context of the ongoing learning session and classify their goal into exactly one of these intents:

1. "QA": Asking a specific factual, academic, or conceptual question.
   Examples: "What is the largest ocean?", "What is polymorphism in Java?", "Why do leaves change color?"
2. "EXPLAIN": Asking to break down, explain, simplify, or demystify a concept or topic, or asking for an example.
   Examples: "Explain recursion in simple terms.", "I don't understand inheritance.", "Can you give me an example?", "Explain that more simply."
3. "QUIZ": Asking to be tested, generate a quiz, create practice multiple-choice questions, or reporting quiz score.
   Examples: "Test me on recursion.", "Create 5 questions on biology.", "Now quiz me.", "I got 2 wrong."
4. "SUMMARIZE": Asking to condense, summarize, or shorten educational text or a passage.
   Examples: "Summarize this paragraph.", "Make this text shorter.", "Summarize what we discussed."
5. "LEARNING_PATH": Asking for a roadmap, curriculum, study schedule, or recommended topics to learn next.
   Examples: "Give me a roadmap to learn SQL.", "What should I learn next?", "Study plan for machine learning."
6. "MULTI_ACTION": The request clearly asks for multiple sequential tasks in order.
   Examples: "Summarize this text and then quiz me.", "Explain photosynthesis and then test me."
7. "CLARIFICATION": The request is ambiguous OR it explicitly refers to prior context that is missing without context.
8. "UNKNOWN": Casual conversation (e.g. "Hello EduGenie", "Hi", "Thanks") OR completely off-topic requests (e.g. "Do something random", "Book a flight").

CONTEXT RESOLUTION INSTRUCTIONS:
- Active Context provides the current topic, recent topics, and active quiz.
- If the user uses referential words like "that", "this", "it", "more simply", "give me an example", or "quiz me", resolve the topic using the Active Context.
- If the user says "Explain that again" or "Quiz me on that" but Active Context has NO topic, mark intent="CLARIFICATION", requires_context=true.
- Return STRICTLY a valid JSON object without markdown formatting.

Format:
{
  "intent": "QA" | "EXPLAIN" | "QUIZ" | "SUMMARIZE" | "LEARNING_PATH" | "MULTI_ACTION" | "CLARIFICATION" | "UNKNOWN",
  "topic": string or null,
  "input_text": string or null,
  "difficulty": "BEGINNER" | "INTERMEDIATE" | "ADVANCED" | null,
  "question_count": integer,
  "language": "ENGLISH",
  "style": "SIMPLE" | null,
  "requires_context": boolean,
  "clarification_prompt": string or null,
  "actions": [
    {
      "intent": "SUMMARIZE",
      "topic": null,
      "depends_on": null
    },
    {
      "intent": "QUIZ",
      "topic": null,
      "depends_on": "previous_result"
    }
  ],
  "reasoning": "brief explanation"
}
"""

def clean_json_text(text: str) -> str:
    """Strips Markdown fences from AI response."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*\n", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n```\s*$", "", text)
    return text.strip()

def _deterministic_context_classifier(
    message: str,
    context: Optional[ContextState] = None
) -> StructuredIntent:
    """
    High-precision deterministic intent analyzer and context resolver used when
    Gemini is unconfigured, offline, or during isolated test runs.
    """
    msg = message.strip()
    msg_lower = msg.lower()
    clean_lower = msg_lower.strip(".?!")

    current_topic = context.current_topic if context else None
    has_active_quiz = bool(context and context.last_quiz)
    active_quiz_topic = context.last_quiz.topic if has_active_quiz else None

    # 1. Multi-Action detection (evaluate composite workflows first)
    multi_patterns = [
        (
            r"summarize\s+(?:this|the)?.*?\s+and\s+(?:then\s+)?(?:generate\s+a\s+quiz|quiz\s+me|test\s+me)",
            [
                ActionItem(intent=IntentType.SUMMARIZE),
                ActionItem(intent=IntentType.QUIZ, depends_on="previous_result")
            ]
        ),
        (
            r"explain\s+(?:the\s+concept\s+of\s+)?(.*?)\s+and\s+(?:then\s+)?(?:quiz|test)\s+me",
            lambda m: [
                ActionItem(intent=IntentType.EXPLAIN, topic=m.group(1).strip() if m.group(1) else current_topic),
                ActionItem(intent=IntentType.QUIZ, topic=m.group(1).strip() if m.group(1) else current_topic, depends_on="previous_result")
            ]
        )
    ]
    for pattern, actions in multi_patterns:
        m = re.search(pattern, msg_lower)
        if m:
            resolved_actions = actions(m) if callable(actions) else actions
            return StructuredIntent(
                intent=IntentType.MULTI_ACTION,
                topic=resolved_actions[0].topic if resolved_actions else current_topic,
                actions=resolved_actions,
                reasoning="Composite multi-action request detected."
            )

    # 2. Quiz Performance Feedback (e.g. "I got 2 wrong", "I missed 1")
    score_match = re.search(r"\b(?:i\s+got|missed)\s+(\d+)\s+(?:wrong|incorrect|questions\s+wrong)\b", msg_lower)
    if score_match or clean_lower in ["i got 2 wrong", "i got 1 wrong", "i got 0 wrong"]:
        if has_active_quiz:
            return StructuredIntent(
                intent=IntentType.QUIZ,
                topic=active_quiz_topic,
                reasoning=f"User reporting performance on active quiz for '{active_quiz_topic}'."
            )
        elif current_topic:
            return StructuredIntent(
                intent=IntentType.QUIZ,
                topic=current_topic,
                reasoning=f"User reporting quiz performance related to current topic '{current_topic}'."
            )

    # 3. Remedial Follow-up (e.g. "Teach me what I got wrong", "Explain what I got wrong")
    if any(p in msg_lower for p in ["teach me what i got wrong", "explain what i got wrong", "review my mistakes"]):
        remedial_topic = active_quiz_topic or current_topic
        if remedial_topic:
            return StructuredIntent(
                intent=IntentType.EXPLAIN,
                topic=f"the core concepts of {remedial_topic}",
                style="SIMPLE",
                reasoning=f"Remedial explanation on quiz topic '{remedial_topic}'."
            )
        else:
            return StructuredIntent(
                intent=IntentType.CLARIFICATION,
                requires_context=True,
                clarification_prompt="Which topic or quiz questions would you like to review?",
                reasoning="Remedial request without previous quiz context."
            )

    # 4. Contextual Follow-up: "Explain that more simply" / "Make it simpler" / "Explain that again"
    simplify_patterns = [
        r"\b(?:explain|clarify|elaborate)\s+(?:that|it)\s+more\s+simply\b",
        r"\bmore\s+simply\b",
        r"\bmake\s+it\s+simpler\b",
        r"\bexplain\s+(?:that|it)\s+again\b",
        r"\bexplain\s+(?:that|it)\b"
    ]
    if any(re.search(p, msg_lower) for p in simplify_patterns):
        if current_topic:
            return StructuredIntent(
                intent=IntentType.EXPLAIN,
                topic=current_topic,
                style="SIMPLE",
                reasoning=f"Resolved follow-up simplification to current topic '{current_topic}'."
            )
        else:
            return StructuredIntent(
                intent=IntentType.CLARIFICATION,
                requires_context=True,
                clarification_prompt="I don't have our previous conversation context yet. Could you please specify which topic you would like me to explain?",
                reasoning="Contextual explanation requested without active topic."
            )

    # 5. Contextual Follow-up: "Give me an example" / "Show an example"
    example_patterns = [
        r"\b(?:give\s+me|show\s+me|provide)\s+(?:an?\s+)?example\b",
        r"\ban?\s+example\s+of\s+that\b"
    ]
    if any(re.search(p, msg_lower) for p in example_patterns):
        if current_topic:
            return StructuredIntent(
                intent=IntentType.EXPLAIN,
                topic=f"an example of {current_topic}",
                reasoning=f"Resolved example request to active topic '{current_topic}'."
            )
        else:
            return StructuredIntent(
                intent=IntentType.CLARIFICATION,
                requires_context=True,
                clarification_prompt="Which concept or topic would you like an example for?",
                reasoning="Example requested without active topic in context."
            )

    # 6. Contextual Follow-up: "Quiz me" / "Test me on that" / "Now quiz me"
    quiz_followup_patterns = [
        r"^now\s+quiz\s+me",
        r"^quiz\s+me\s+on\s+(?:it|this|that)",
        r"^test\s+me\s+on\s+(?:it|this|that)",
        r"^now\s+quiz\s+me$",
        r"^quiz\s+me$",
        r"^test\s+me$"
    ]
    if any(re.search(p, clean_lower) for p in quiz_followup_patterns):
        if current_topic:
            return StructuredIntent(
                intent=IntentType.QUIZ,
                topic=current_topic,
                question_count=3,
                confidence=1.0,
                reasoning=f"Resolved quiz request to active topic '{current_topic}'."
            )
        else:
            return StructuredIntent(
                intent=IntentType.CLARIFICATION,
                requires_context=True,
                confidence=1.0,
                clarification_prompt="I don't have our previous conversation context yet. What topic would you like to be quizzed on?",
                reasoning="Quiz requested without active topic in context."
            )

    # 7. Contextual Follow-up: "What should I learn next?"
    next_step_patterns = [
        r"\bwhat\s+should\s+i\s+learn\s+next\b",
        r"\bwhat\s+next\b",
        r"\bwhere\s+do\s+i\s+go\s+from\s+here\b"
    ]
    if any(re.search(p, msg_lower) for p in next_step_patterns):
        if current_topic:
            return StructuredIntent(
                intent=IntentType.LEARNING_PATH,
                topic=f"What to learn after mastering {current_topic}",
                confidence=1.0,
                reasoning=f"Resolved next-steps roadmap following current topic '{current_topic}'."
            )
        else:
            return StructuredIntent(
                intent=IntentType.LEARNING_PATH,
                topic=msg,
                confidence=1.0,
                reasoning="General learning roadmap request."
            )

    # 8. Conversational / Greetings
    greetings = ["hello", "hi", "hey", "greetings", "good morning", "good evening", "hello edugenie", "hi edugenie"]
    if clean_lower in greetings or any(clean_lower.startswith(g) for g in ["hello edugenie", "hi edugenie", "hey edugenie"]):
        return StructuredIntent(
            intent=IntentType.UNKNOWN,
            confidence=1.0,
            reasoning="Conversational greeting."
        )

    # 9. Off-topic / Unclear / Random
    offtopic_starters = ["do something", "something random", "random", "play ", "sing ", "tell a joke", "book ", "buy "]
    if clean_lower in ["do something random", "random", "asdf", "test"] or any(clean_lower.startswith(o) for o in offtopic_starters):
        return StructuredIntent(
            intent=IntentType.UNKNOWN,
            confidence=1.0,
            reasoning="Off-topic or unrecognized request."
        )

    # 10. Ambiguous requests (e.g. "Tell me more about Python")
    ambiguous_patterns = [
        r"^tell\s+me\s+more\s+about\s+(.+)$",
        r"^more\s+about\s+(.+)$",
        r"^tell\s+me\s+about\s+(.+)$"
    ]
    for pat in ambiguous_patterns:
        m = re.match(pat, msg_lower)
        if m:
            topic = m.group(1).strip().strip(".?!")
            return StructuredIntent(
                intent=IntentType.CLARIFICATION,
                topic=topic,
                confidence=1.0,
                clarification_prompt=(
                    f"What would you like to do with '{topic}'? You can ask a specific question, "
                    "request a simplified concept explanation, generate a practice quiz, or get a structured learning roadmap."
                ),
                reasoning="Broad/ambiguous request requiring clarification."
            )

    # 11. Summarization
    summary_keywords = ["summarize", "give me a summary", "make this shorter", "make this paragraph shorter", "make this chapter shorter", "make this text shorter", "condense this", "tldr"]
    if any(msg_lower.startswith(k) for k in summary_keywords):
        text = re.sub(r"(?i)^(?:summarize\s+this\s+paragraph[:\s]*|make\s+this\s+(?:paragraph|chapter|text)\s+shorter[:\s]*|give\s+me\s+a\s+summary\s+of[:\s]*|summarize[:\s]*)", "", msg).strip()
        return StructuredIntent(
            intent=IntentType.SUMMARIZE,
            input_text=text or msg,
            confidence=1.0,
            reasoning="User requested text summarization."
        )

    # 12. Learning Path / Roadmap
    path_keywords = ["roadmap", "learning path", "curriculum", "study plan", "how to learn", "how should i learn", "what to learn to master", "where to start learning"]
    if any(k in msg_lower for k in path_keywords):
        topic = re.sub(r"(?i)^(?:give\s+me\s+a\s+roadmap\s+to\s+learn|roadmap\s+for|study\s+plan\s+for|how\s+to\s+learn|how\s+should\s+i\s+learn)\s*", "", msg).strip().strip(".?!")
        return StructuredIntent(
            intent=IntentType.LEARNING_PATH,
            topic=topic or msg,
            confidence=1.0,
            reasoning="User requested a learning path or study curriculum."
        )

    # 13. Explicit Quiz
    quiz_keywords = ["test me on", "generate a quiz", "create a quiz", "quiz me on", "quiz about", "practice questions", "give me a quiz"]
    if any(k in msg_lower for k in quiz_keywords):
        topic = re.sub(r"(?i)^(?:test\s+me\s+on|quiz\s+me\s+on|generate\s+a\s+quiz\s+about|create\s+a\s+quiz\s+on|give\s+me\s+a\s+quiz\s+on)\s*", "", msg).strip().strip(".?!")
        return StructuredIntent(
            intent=IntentType.QUIZ,
            topic=topic or msg,
            question_count=3,
            confidence=1.0,
            reasoning="User requested a quiz or self-assessment."
        )

    # 14. Concept Explanation
    explain_keywords = ["explain", "i don't understand", "i do not understand", "teach me", "clarify", "demystify", "how does"]
    if any(k in msg_lower for k in explain_keywords):
        topic = re.sub(r"(?i)^(?:explain\s+|i\s+don'?t\s+understand\s+|teach\s+me\s+|clarify\s+)", "", msg).strip().strip(".?!")
        style = "SIMPLE" if "simple" in msg_lower or "beginner" in msg_lower else None
        return StructuredIntent(
            intent=IntentType.EXPLAIN,
            topic=topic or msg,
            style=style,
            confidence=1.0,
            reasoning="User requested a concept explanation."
        )

    # 15. General Q&A (questions starting with What, Who, Where, Why, When, Which, Is, Can, Does, or ending with '?')
    qa_starters = ["what", "who", "where", "why", "when", "which", "how many", "is", "are", "can", "does", "tell me about"]
    if any(msg_lower.startswith(s + " ") for s in qa_starters) or msg.endswith("?"):
        # Extract meaningful subject if question starts with "What is X"
        m = re.match(r"(?i)^what\s+is\s+(.+?)\??$", msg)
        topic = m.group(1).strip() if m else msg
        return StructuredIntent(
            intent=IntentType.QA,
            topic=topic,
            confidence=1.0,
            reasoning="Factual or academic question."
        )

    # Default fallback to Q&A (marked with low confidence 0.4 so ambiguous inputs can be routed by Gemini)
    return StructuredIntent(
        intent=IntentType.QA,
        topic=msg,
        confidence=0.4,
        reasoning="Default academic question classification."
    )

def classify_intent(
    message: str,
    context: Optional[ContextState] = None,
    recent_history: Optional[List[ConversationMessage]] = None
) -> StructuredIntent:
    """
    Classifies user message into a StructuredIntent.
    Uses high-precision local pre-router with 0 Gemini calls for clear intents.
    Falls back to Gemini intent classifier only for ambiguous inputs.
    """
    if not message or not message.strip():
        return StructuredIntent(
            intent=IntentType.UNKNOWN,
            confidence=1.0,
            reasoning="Empty input received."
        )

    clean_message = message.strip()

    # 1. Fast Local Intent Pre-Router (0 network calls, sub-millisecond)
    local_intent = _deterministic_context_classifier(clean_message, context=context)
    if local_intent.confidence >= 0.8:
        logger.info(
            f"⚡ [FAST-ROUTER] Intent '{local_intent.intent}' resolved locally (0 Gemini calls, Topic: '{local_intent.topic}')"
        )
        return local_intent

    # If Gemini is not configured, return the deterministic result directly
    if not is_gemini_configured():
        return local_intent

    # 2. Ambiguous query fallback: call Gemini intent classifier
    logger.info("🤔 [GEMINI-ROUTER] Intent ambiguous; invoking Gemini intent classifier...")

    context_lines = []
    if context:
        if context.current_topic:
            context_lines.append(f"Current Topic: {context.current_topic}")
        if context.recent_topics:
            context_lines.append(f"Recent Topics: {', '.join(context.recent_topics[-3:])}")
        if context.last_quiz:
            context_lines.append(f"Active Quiz: {context.last_quiz.topic} (Total: {context.last_quiz.total})")

    history_lines = []
    if recent_history:
        for m in recent_history[-6:]:
            history_lines.append(f"{m.role.capitalize()}: {m.content}")

    context_block = "\n".join(context_lines) if context_lines else "No active topic."
    history_block = "\n".join(history_lines) if history_lines else "No previous messages."

    prompt = (
        f"{SYSTEM_CLASSIFIER_PROMPT}\n\n"
        f"--- ACTIVE CONTEXT ---\n{context_block}\n\n"
        f"--- RECENT CONVERSATION HISTORY ---\n{history_block}\n\n"
        f"USER MESSAGE:\n\"{clean_message}\""
    )

    try:
        raw_output = generate_gemini_text(prompt)
        cleaned = clean_json_text(raw_output)
        data = json.loads(cleaned)
        structured = StructuredIntent(**data)
        return structured
    except Exception as e:
        logger.warning(f"Gemini intent classification fallback to deterministic ({e}).")
        return local_intent
