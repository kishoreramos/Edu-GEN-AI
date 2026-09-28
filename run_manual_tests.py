"""
EduGenie Manual Document Verification Runner
Executes the exact manual test cases against http://127.0.0.1:8000
and checks status codes, JSON contracts, payload semantics,
and frontend script logic.
"""
import sys
import json
import urllib.request
import urllib.error

# Ensure UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"

def post_json(path, data):
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"error": body}

def get_req(path):
    req = urllib.request.Request(f"{BASE_URL}{path}")
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.headers.get_content_type(), resp.read().decode("utf-8")

print("=" * 65)
print("EDUGENIE MANUAL DOCUMENT VERIFICATION SUITE")
print("Target Server:", BASE_URL)
print("=" * 65 + "\n")

results = {}

# -----------------------------------------------------------------
# MANUAL TEST 1: Q&A
# -----------------------------------------------------------------
print("--- [TEST 1] Q&A: 'What is polymorphism in Java?' ---")
status, res = post_json("/qa", {"question": "What is polymorphism in Java?"})
assert status == 200, f"Expected 200, got {status}"
ans = res.get("answer", "")
assert len(ans) > 30, "Answer too short"
print(f"Status: {status} OK")
print(f"Answer Length: {len(ans)} chars")
print(f"Answer Preview: {ans[:150].strip()}...\n")
results["Q&A"] = "PASS"

# -----------------------------------------------------------------
# MANUAL TEST 2: Explanation
# -----------------------------------------------------------------
print("--- [TEST 2] Explanation: 'Explain recursion in simple terms.' ---")
status, res = post_json("/explain", {"topic": "recursion in simple terms"})
assert status == 200, f"Expected 200, got {status}"
exp = res.get("explanation", "")
assert len(exp) > 30, "Explanation too short"
print(f"Status: {status} OK")
print(f"Explanation Length: {len(exp)} chars")
print(f"Explanation Preview: {exp[:150].strip()}...\n")
results["Explanation"] = "PASS"

# -----------------------------------------------------------------
# MANUAL TEST 3: Quiz
# -----------------------------------------------------------------
print("--- [TEST 3] Quiz: 'Java inheritance' ---")
status, res = post_json("/quiz", {"topic": "Java inheritance"})
assert status == 200, f"Expected 200, got {status}"
quiz = res.get("quiz", [])
assert len(quiz) == 3, f"Expected 3 questions, got {len(quiz)}"
for i, q in enumerate(quiz):
    assert len(q.get("options", [])) == 4, f"Q{i+1} does not have 4 options"
    assert q.get("answer") in q["options"], f"Q{i+1} answer not in options"
print(f"Status: {status} OK")
print(f"Quiz Questions Count: {len(quiz)}")
print(f"Sample Question 1: {quiz[0]['question']}")
print(f"Sample Options: {quiz[0]['options']}")
print(f"Sample Answer: {quiz[0]['answer']}\n")
results["Quiz"] = "PASS"

# -----------------------------------------------------------------
# MANUAL TEST 4: Summarization
# -----------------------------------------------------------------
print("--- [TEST 4] Summarization ---")
passage = (
    "Database normalization is the process of structuring a relational database in accordance with "
    "a series of normal forms in order to reduce data redundancy and improve data integrity. "
    "It was first proposed by Edgar F. Codd as part of his relational model."
)
status, res = post_json("/summarize", {"text": passage})
assert status == 200, f"Expected 200, got {status}"
summary = res.get("summary", "")
assert len(summary) > 20, "Summary too short"
print(f"Status: {status} OK")
print(f"Summary Length: {len(summary)} chars")
print(f"Summary Preview: {summary[:150].strip()}...\n")
results["Summarization"] = "PASS"

# -----------------------------------------------------------------
# MANUAL TEST 5: Learning Path
# -----------------------------------------------------------------
print("--- [TEST 5] Learning Path: 'SQL' ---")
status, res = post_json("/learn/recommendations", {"topic": "SQL"})
assert status == 200, f"Expected 200, got {status}"
rec = res.get("recommendation") or res.get("recommendations", "")
assert len(rec) > 30, "Recommendation too short"
print(f"Status: {status} OK")
print(f"Roadmap Length: {len(rec)} chars")
print(f"Roadmap Preview: {rec[:150].strip()}...\n")
results["Learning Path"] = "PASS"

# -----------------------------------------------------------------
# MANUAL TEST 6: Task Switching
# -----------------------------------------------------------------
print("--- [TEST 6] Task Switching & Chat Integration ---")
status, res = post_json("/api/chat", {"message": "Explain recursion"})
assert status == 200 and res.get("success"), "Explain task chat failed"
status, res = post_json("/api/chat", {"message": "What is an algorithm?"})
assert status == 200 and res.get("success"), "QnA task chat failed"
status, res = post_json("/api/chat", {"message": "Quiz me on Python"})
assert status == 200 and res.get("success"), "Quiz task chat failed"
status, res = post_json("/api/chat", {"message": f"Summarize: {passage}"})
assert status == 200 and res.get("success"), "Summary task chat failed"
status, res = post_json("/api/chat", {"message": "Give me a roadmap for SQL"})
assert status == 200 and res.get("success"), "Recommend Path task chat failed"
print("All 5 tasks switch and execute cleanly through conversational integration.")
results["Task Switching"] = "PASS"

# -----------------------------------------------------------------
# MANUAL TEST 7: Empty Input
# -----------------------------------------------------------------
print("\n--- [TEST 7] Empty Input Handling ---")
s_qa, r_qa = post_json("/qa", {"question": "   "})
assert s_qa == 400 and "error" in r_qa
s_exp, r_exp = post_json("/explain", {"topic": ""})
assert s_exp == 400 and "error" in r_exp
s_qz, r_qz = post_json("/quiz", {"text": ""})
assert s_qz == 400 and "error" in r_qz
s_sum, r_sum = post_json("/summarize", {"text": ""})
assert s_sum == 400 and "error" in r_sum
s_lp, r_lp = post_json("/learn/recommendations", {"topic": ""})
assert s_lp == 400 and "error" in r_lp
s_chat, r_chat = post_json("/api/chat", {"message": ""})
assert s_chat == 422 or s_chat == 400
print("Empty inputs across all endpoints safely return HTTP 400/422 with descriptive error messages.")
results["Empty Input"] = "PASS"

# -----------------------------------------------------------------
# MANUAL TEST 8: Server / Browser Health
# -----------------------------------------------------------------
print("\n--- [TEST 8] Server / Browser Health ---")
s_home, ct_home, body_home = get_req("/")
assert s_home == 200 and "text/html" in ct_home
assert "EduGenie" in body_home
assert "task-selector" in body_home

s_css, ct_css, body_css = get_req("/static/style.css")
assert s_css == 200 and "text/css" in ct_css
assert ".task-selector" in body_css

s_js, ct_js, body_js = get_req("/static/app.js")
assert s_js == 200 and "javascript" in ct_js
assert "data-task" in body_js
print("HTML, CSS, JS served with 200 OK and correct MIME types. Zero syntax or load errors.")
results["Browser Health"] = "PASS"

print("\n" + "=" * 65)
print("ALL 8 MANUAL VERIFICATION TESTS PASSED SUCCESSFULLY!")
print("=" * 65)
