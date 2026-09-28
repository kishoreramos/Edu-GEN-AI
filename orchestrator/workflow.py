# EduGenie Multi-Action Sequential Workflow Engine
import logging
from typing import List, Dict, Any

from .schemas import IntentType, StructuredIntent, ActionItem, ToolResult
try:
    from ..explanation_module import explain_topic
    from ..summary_module import summarize_text
    from ..quiz_module import generate_quiz
    from ..learning_path import get_learning_recommendations
    from ..qna import answer_question_with_gemini
except ImportError:
    from explanation_module import explain_topic
    from summary_module import summarize_text
    from quiz_module import generate_quiz
    from learning_path import get_learning_recommendations
    from qna import answer_question_with_gemini

logger = logging.getLogger("EduGenie.Workflow")

def execute_multi_action_workflow(intent: StructuredIntent, raw_message: str) -> ToolResult:
    """
    Executes a deterministic sequential multi-step workflow.
    Allows downstream actions to consume the results produced by upstream actions.
    """
    actions = intent.actions
    if not actions:
        # Fallback default: if multi-action was flagged without steps, default to Explain
        logger.warning("MULTI_ACTION triggered with empty action list; falling back to Explanation.")
        explanation = explain_topic(intent.topic or raw_message)
        return ToolResult(
            success=True,
            tool="EXPLAIN",
            content=explanation,
            data={"topic": intent.topic or raw_message, "explanation": explanation}
        )

    step_results: List[Dict[str, Any]] = []
    last_output_text: str = ""
    summary_text: str = ""
    explanation_text: str = ""
    quiz_data: List[Dict[str, Any]] = []

    for idx, action in enumerate(actions):
        step_number = idx + 1
        logger.info(f"Executing workflow step {step_number}/{len(actions)}: {action.intent}")

        # Determine input payload for this step
        if action.depends_on == "previous_result" and last_output_text:
            current_input = last_output_text
        else:
            current_input = action.input_text or action.topic or intent.input_text or intent.topic or raw_message

        # Execute action using existing EduGenie capabilities
        if action.intent == IntentType.SUMMARIZE:
            summary = summarize_text(current_input)
            last_output_text = summary
            summary_text = summary
            step_results.append({
                "step": step_number,
                "action": "SUMMARIZE",
                "result": summary
            })

        elif action.intent == IntentType.EXPLAIN:
            explanation = explain_topic(current_input)
            last_output_text = explanation
            explanation_text = explanation
            step_results.append({
                "step": step_number,
                "action": "EXPLAIN",
                "result": explanation
            })

        elif action.intent == IntentType.QUIZ:
            # If quiz depends on previous summary or explanation, pass the generated content
            quiz = generate_quiz(current_input)
            quiz_data = quiz
            last_output_text = f"Quiz with {len(quiz)} questions generated."
            step_results.append({
                "step": step_number,
                "action": "QUIZ",
                "result": quiz
            })

        elif action.intent == IntentType.LEARNING_PATH:
            path = get_learning_recommendations(current_input)
            last_output_text = path
            step_results.append({
                "step": step_number,
                "action": "LEARNING_PATH",
                "result": path
            })

        elif action.intent == IntentType.QA:
            answer = answer_question_with_gemini(current_input)
            last_output_text = answer
            step_results.append({
                "step": step_number,
                "action": "QA",
                "result": answer
            })

    # Compose unified response text
    reply_lines = ["I have completed your requested multi-step workflow:\n"]
    for s in step_results:
        action_name = s["action"]
        if action_name == "SUMMARIZE":
            reply_lines.append(f"### 📝 Summary:\n{s['result']}\n")
        elif action_name == "EXPLAIN":
            reply_lines.append(f"### 💡 Concept Explanation:\n{s['result']}\n")
        elif action_name == "QUIZ":
            reply_lines.append(f"### 🎯 Practice Quiz:\nGenerated {len(s['result'])} questions based on the content above.\n")
        elif action_name == "LEARNING_PATH":
            reply_lines.append(f"### 🗺️ Learning Roadmap:\n{s['result']}\n")
        elif action_name == "QA":
            reply_lines.append(f"### ❓ Answer:\n{s['result']}\n")

    unified_reply = "\n".join(reply_lines).strip()

    return ToolResult(
        success=True,
        tool="MULTI_ACTION",
        content=unified_reply,
        data={
            "steps": step_results,
            "summary": summary_text,
            "explanation": explanation_text,
            "quiz": quiz_data
        }
    )
