import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, ".")

from config import generate_gemini_text, GEMINI_MODEL, is_gemini_configured
from qna import answer_question_with_gemini
from explanation_module import explain_topic
from quiz_module import generate_quiz

print(f"API Key Configured: {is_gemini_configured()}")
print(f"Centrally Configured Model: {GEMINI_MODEL}")

print("\n=== Smoke Test 1: What is Python? ===")
ans1 = answer_question_with_gemini("What is Python?")
print(f"Response 1:\n{ans1[:300]}")

time.sleep(3)

print("\n=== Smoke Test 2: Explain recursion simply. ===")
ans2 = explain_topic("recursion")
print(f"Response 2:\n{ans2[:300]}")

time.sleep(3)

print("\n=== Smoke Test 3: Give me a quiz on Java inheritance. ===")
ans3 = generate_quiz("Java inheritance")
print(f"Quiz Questions Count: {len(ans3)}")
for i, q in enumerate(ans3, 1):
    print(f"Question {i}: {q['question']}")
    print(f"Options: {q['options']}")
    print(f"Correct Answer: {q['answer']}\n")
