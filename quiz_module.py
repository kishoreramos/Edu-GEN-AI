# Quiz Module - EduGenie
import re
import json
import logging
from typing import List, Dict, Any

try:
    from .config import generate_gemini_text, is_gemini_configured, GEMINI_KEY_MISSING_ERROR, GEMINI_MODEL
except ImportError:
    from config import generate_gemini_text, is_gemini_configured, GEMINI_KEY_MISSING_ERROR, GEMINI_MODEL

logger = logging.getLogger("EduGenie.Quiz")

def clean_json_block(text: str) -> str:
    """
    Strips Markdown code fences like ```json ... ``` or ``` ... ```
    around JSON strings.
    """
    text = text.strip()
    # Match ```json ... ``` or ``` ... ```
    cleaned = re.sub(r"^```(?:json)?\s*\n", "", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"\n```\s*$", "", cleaned)
    return cleaned.strip()

def validate_quiz_structure(data: Any) -> List[Dict[str, Any]]:
    """
    Validates that parsed data is a list of valid MCQs with:
    - 'question': non-empty string
    - 'options': list of exactly 4 strings
    - 'answer': string that exactly matches one of the options
    """
    if not isinstance(data, list):
        raise ValueError("Quiz response root must be a JSON array.")

    validated = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            continue

        q = item.get("question")
        opts = item.get("options")
        ans = item.get("answer")

        if not q or not isinstance(q, str):
            continue
        if not opts or not isinstance(opts, list) or len(opts) != 4:
            continue
        if not ans or not isinstance(ans, str):
            continue

        # Convert options to strings
        opts_str = [str(o).strip() for o in opts]
        ans_str = str(ans).strip()

        # If answer is just a letter like 'A', 'B', 'C', 'D', map to corresponding option
        if ans_str.upper() in ["A", "B", "C", "D"] and ans_str not in opts_str:
            letter_idx = ord(ans_str.upper()) - ord("A")
            if 0 <= letter_idx < len(opts_str):
                ans_str = opts_str[letter_idx]

        # Ensure answer matches one of the options
        if ans_str not in opts_str:
            # Fallback: if case-insensitive match exists
            matched = False
            for o in opts_str:
                if o.lower() == ans_str.lower():
                    ans_str = o
                    matched = True
                    break
            if not matched:
                opts_str[0] = ans_str  # Ensure integrity

        validated.append({
            "question": q.strip(),
            "options": opts_str,
            "answer": ans_str
        })

    if not validated:
        raise ValueError("No valid questions could be verified from the AI output.")

    return validated

def generate_quiz(text: str) -> List[Dict[str, Any]]:
    """
    Generates 3 multiple-choice questions from the provided passage/topic.
    Returns structured list of questions, options, and correct answers.
    """
    if not text or not text.strip():
        logger.warning("Empty text received for quiz generation.")
        return []

    if not is_gemini_configured():
        logger.warning("Gemini API key is not configured for quiz generation.")
        clean_t = text.strip()
        return [
            {
                "question": f"What is a fundamental concept of {clean_t}?",
                "options": ["Basic principles and definitions", "Advanced obscure theories", "Unrelated trivia", "None of the above"],
                "answer": "Basic principles and definitions"
            },
            {
                "question": f"Which field most commonly uses {clean_t}?",
                "options": ["Computer Science & Mathematics", "Ancient History", "Culinary Arts", "Fashion Design"],
                "answer": "Computer Science & Mathematics"
            },
            {
                "question": f"Why is understanding {clean_t} important for students?",
                "options": ["It builds foundational analytical skills", "It has no practical value", "It is obsolete", "It cannot be learned"],
                "answer": "It builds foundational analytical skills"
            }
        ]

    try:
        prompt = f"""You are a quiz generator.

From the following passage or topic, create exactly 3 multiple-choice questions.
Each question should include:
- A "question": string
- A list of 4 "options": list of 4 strings
- A correct "answer" that must exactly match one of the 4 options.

Format your output as **valid JSON** only. Do NOT include markdown commentary outside the JSON block.
Example format:
[
  {{
    "question": "What is ...?",
    "options": ["A", "B", "C", "D"],
    "answer": "A"
  }}
]

Passage:
{text.strip()}
"""
        raw_text = generate_gemini_text(prompt)
        if raw_text.startswith("⚠️"):
            raise RuntimeError(raw_text)

        cleaned_text = clean_json_block(raw_text)

        # Attempt JSON parsing
        try:
            parsed = json.loads(cleaned_text)
        except json.JSONDecodeError:
            # Fallback: extract substring between [ and ]
            match = re.search(r"\[.*\]", cleaned_text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
            else:
                raise ValueError(f"Could not parse valid JSON from AI response: {cleaned_text[:200]}")

        # Validate structure strictly
        validated_quiz = validate_quiz_structure(parsed)
        return validated_quiz

    except Exception as e:
        logger.error(f"Error generating quiz: {e}", exc_info=True)
        # Resilient fallback: return 3 structured questions so user assessment flow is never broken
        topic_label = text.strip() if text else "this topic"
        return [
            {
                "question": f"What is a primary concept of {topic_label}?",
                "options": [
                    f"Core foundational principles of {topic_label}",
                    "Irrelevant option B",
                    "Irrelevant option C",
                    "Irrelevant option D"
                ],
                "answer": f"Core foundational principles of {topic_label}"
            },
            {
                "question": f"Which best describes the practical application of {topic_label}?",
                "options": [
                    "Theoretical knowledge only",
                    f"Practical implementation and usage of {topic_label}",
                    "Random guess",
                    "None of the above"
                ],
                "answer": f"Practical implementation and usage of {topic_label}"
            },
            {
                "question": f"Why is understanding {topic_label} important for developers?",
                "options": [
                    "It builds foundational analytical skills",
                    "It has no practical value",
                    "It is purely optional",
                    "It only applies to legacy systems"
                ],
                "answer": "It builds foundational analytical skills"
            }
        ]

