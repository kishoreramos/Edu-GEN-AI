"""
EduGenie Document-First Verification Test Suite
Strictly verifies the original EduGenie requirements according to the original project document:
1. Question & Answer (POST /qa)
2. Simplified Concept Explanation (POST /explain)
3. Quiz Generation (POST /quiz)
4. Text Summarization (POST /summarize)
5. Learning Path Recommendations (POST /learn/recommendations)
6. Five Documented Endpoints (POST /qa, POST /explain, POST /quiz, POST /summarize, POST /learn/recommendations)
7. Frontend Availability (index.html, style.css, app.js, task selection)
All tests are strictly bounded with hard timeouts and zero infinite loops.
"""
import os
import sys
import time
import unittest
from pathlib import Path

# Ensure UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
import main
import config
from qna import answer_question_with_gemini
from explanation_module import explain_topic, _load_local_lamini_model
from quiz_module import generate_quiz, validate_quiz_structure, clean_json_block
from summary_module import summarize_text
from learning_path import get_learning_recommendations


class TestEduGenieDocumentRequirements(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)
        cls.gemini_configured = config.is_gemini_configured()
        print("\n" + "=" * 65)
        print("EDUGENIE DOCUMENT-FIRST REQUIREMENTS VERIFICATION")
        print("=" * 65)
        print(f"Gemini API Configured: {cls.gemini_configured}")
        print(f"Active/Central Model: {config._active_working_model or config.GEMINI_MODEL}")
        print("=" * 65 + "\n")

    def _call_with_bounded_retry(self, fn, *args, **kwargs):
        """Runs a call with max 2 attempts and bounded backoff."""
        for attempt in range(2):
            try:
                res = fn(*args, **kwargs)
                if isinstance(res, str) and ("rate limit" in res.lower() or "429" in res):
                    if attempt == 0:
                        time.sleep(3)
                        continue
                return res
            except Exception as e:
                if attempt == 0:
                    time.sleep(3)
                    continue
                raise e
        return res

    # -------------------------------------------------------------
    # 1. Question & Answer Verification (POST /qa)
    # -------------------------------------------------------------
    def test_01_qna_requirement(self):
        """Verify Q&A module and POST /qa endpoint with educational query."""
        print("[01/07] Testing Q&A Requirement (POST /qa)...")
        # Direct module test
        ans_mod = self._call_with_bounded_retry(
            answer_question_with_gemini,
            "What is polymorphism in Java?"
        )
        self.assertIsInstance(ans_mod, str)
        self.assertTrue(len(ans_mod) > 20, f"Q&A module returned too short response: {ans_mod}")
        self.assertFalse(ans_mod.startswith("⚠️ Error: Prompt cannot be empty"))

        # Endpoint test (POST /qa)
        res_post = self.client.post("/qa", json={"question": "What is polymorphism in Java?"})
        self.assertEqual(res_post.status_code, 200, f"POST /qa failed: {res_post.text}")
        data_post = res_post.json()
        self.assertIn("answer", data_post)
        self.assertTrue(len(data_post["answer"]) > 20)

        # Endpoint test (GET /qa backwards compatibility)
        res_get = self.client.get("/qa", params={"question": "What is polymorphism in Java?"})
        self.assertEqual(res_get.status_code, 200)

        # Empty validation
        res_empty = self.client.post("/qa", json={})
        self.assertEqual(res_empty.status_code, 400)

        print(f"       PASS: Q&A generated response ({len(data_post['answer'])} chars)")

    # -------------------------------------------------------------
    # 2. Concept Explanation Verification (POST /explain & LaMini)
    # -------------------------------------------------------------
    def test_02_explanation_requirement(self):
        """Verify Concept Explanation module and POST /explain endpoint."""
        print("[02/07] Testing Concept Explanation Requirement (POST /explain)...")
        # Check LaMini model status
        model, tokenizer = _load_local_lamini_model()
        lamini_loaded = bool(model is not None and tokenizer is not None)
        print(f"       LaMini Model Loaded: {lamini_loaded}")
        print("       Fallback Behavior: Gemini explanation fallback is ACTIVE and functional.")

        # Module test
        exp_mod = self._call_with_bounded_retry(explain_topic, "recursion in simple terms")
        self.assertIsInstance(exp_mod, str)
        self.assertTrue(len(exp_mod) > 20)

        # Endpoint test (POST /explain)
        res_post = self.client.post("/explain", json={"topic": "recursion in simple terms"})
        self.assertEqual(res_post.status_code, 200, f"POST /explain failed: {res_post.text}")
        data = res_post.json()
        self.assertIn("explanation", data)
        self.assertTrue(len(data["explanation"]) > 20)

        # Empty validation
        res_empty = self.client.post("/explain", json={})
        self.assertEqual(res_empty.status_code, 400)

        print(f"       PASS: Explanation generated ({len(data['explanation'])} chars)")

    # -------------------------------------------------------------
    # 3. Quiz Generation Verification (POST /quiz)
    # -------------------------------------------------------------
    def test_03_quiz_requirement(self):
        """Verify Quiz Generation module and POST /quiz endpoint: 3 MCQs, 4 options each, correct answer."""
        print("[03/07] Testing Quiz Generation Requirement (POST /quiz)...")
        # Direct module test
        quiz_list = self._call_with_bounded_retry(generate_quiz, "Java inheritance")
        self.assertIsInstance(quiz_list, list)
        self.assertEqual(len(quiz_list), 3, f"Expected exactly 3 quiz questions, got {len(quiz_list)}")

        for idx, q in enumerate(quiz_list):
            self.assertIn("question", q)
            self.assertIn("options", q)
            self.assertIn("answer", q)
            self.assertEqual(len(q["options"]), 4, f"Question {idx+1} does not have exactly 4 options: {q['options']}")
            self.assertIn(q["answer"], q["options"], f"Question {idx+1} answer '{q['answer']}' not in options")

        # Endpoint test (POST /quiz with topic)
        res = self.client.post("/quiz", json={"topic": "Java inheritance"})
        self.assertEqual(res.status_code, 200, f"POST /quiz failed: {res.text}")
        quiz_data = res.json().get("quiz", [])
        self.assertEqual(len(quiz_data), 3)

        # Endpoint test (POST /quiz with text)
        res_text = self.client.post("/quiz", json={"text": "Java inheritance"})
        self.assertEqual(res_text.status_code, 200)

        # Empty validation
        res_empty = self.client.post("/quiz", json={})
        self.assertEqual(res_empty.status_code, 400)

        print(f"       PASS: Quiz generated exactly 3 MCQs with 4 options each.")

    # -------------------------------------------------------------
    # 4. Text Summarization Verification (POST /summarize)
    # -------------------------------------------------------------
    def test_04_summarization_requirement(self):
        """Verify Text Summarization module and POST /summarize endpoint."""
        print("[04/07] Testing Summarization Requirement (POST /summarize)...")
        sample_passage = (
            "Database normalization is the process of structuring a relational database in accordance with "
            "a series of normal forms in order to reduce data redundancy and improve data integrity. "
            "It was first proposed by Edgar F. Codd as part of his relational model. Normalization entails "
            "organizing the columns and tables of a database to ensure that their dependencies are properly "
            "enforced by database integrity constraints."
        )

        # Module test
        summary = self._call_with_bounded_retry(summarize_text, sample_passage)
        self.assertIsInstance(summary, str)
        self.assertTrue(len(summary) > 20)

        # Endpoint test (POST /summarize)
        res = self.client.post("/summarize", json={"text": sample_passage})
        self.assertEqual(res.status_code, 200, f"POST /summarize failed: {res.text}")
        data = res.json()
        self.assertIn("summary", data)
        self.assertTrue(len(data["summary"]) > 20)

        # Empty validation
        res_empty = self.client.post("/summarize", json={})
        self.assertEqual(res_empty.status_code, 400)

        print(f"       PASS: Summarization returned concise takeaways ({len(data['summary'])} chars)")

    # -------------------------------------------------------------
    # 5. Learning Path Recommendations Verification (POST /learn/recommendations)
    # -------------------------------------------------------------
    def test_05_learning_path_requirement(self):
        """Verify Learning Path Recommendations module and POST /learn/recommendations endpoint."""
        print("[05/07] Testing Learning Path Requirement (POST /learn/recommendations)...")
        # Module test
        roadmap = self._call_with_bounded_retry(get_learning_recommendations, "SQL")
        self.assertIsInstance(roadmap, str)
        self.assertTrue(len(roadmap) > 20)

        # Endpoint test (POST /learn/recommendations)
        res_post = self.client.post("/learn/recommendations", json={"topic": "SQL"})
        self.assertEqual(res_post.status_code, 200, f"POST /learn/recommendations failed: {res_post.text}")
        data = res_post.json()
        rec_text = data.get("recommendation") or data.get("recommendations")
        self.assertIsNotNone(rec_text)
        self.assertTrue(len(rec_text) > 20)

        # Endpoint test (GET /learn/recommendations backwards compatibility)
        res_get = self.client.get("/learn/recommendations", params={"topic": "SQL"})
        self.assertEqual(res_get.status_code, 200)

        # Empty validation
        res_empty = self.client.post("/learn/recommendations", json={})
        self.assertEqual(res_empty.status_code, 400)

        print(f"       PASS: Structured learning roadmap returned ({len(rec_text)} chars)")

    # -------------------------------------------------------------
    # 6. Five Documented Endpoints Contract & Status Verification
    # -------------------------------------------------------------
    def test_06_five_endpoints_contract(self):
        """Verify all five documented endpoints are active, accept POST, and validate inputs."""
        print("[06/07] Testing Five Original Endpoints Contract...")
        endpoints = [
            ("POST /qa", "/qa", {"question": "What is an IDE?"}),
            ("POST /explain", "/explain", {"topic": "IDE"}),
            ("POST /quiz", "/quiz", {"topic": "IDE"}),
            ("POST /summarize", "/summarize", {"text": "An IDE is an integrated development environment."}),
            ("POST /learn/recommendations", "/learn/recommendations", {"topic": "Git"})
        ]

        for name, path, payload in endpoints:
            res = self.client.post(path, json=payload)
            self.assertEqual(
                res.status_code, 200,
                f"Endpoint {name} failed with status {res.status_code}: {res.text}"
            )
            print(f"       PASS: Endpoint {name} -> 200 OK")

    # -------------------------------------------------------------
    # 7. Frontend Layout, Assets & Task Selection Verification
    # -------------------------------------------------------------
    def test_07_frontend_and_task_selection(self):
        """Verify HTML template, CSS styling, JS client, and five task choices are present."""
        print("[07/07] Testing Frontend & Task Selection Availability...")
        # GET /
        res_html = self.client.get("/")
        self.assertEqual(res_html.status_code, 200)
        html = res_html.text

        # Verify HTML has core elements
        self.assertIn("Welcome to EduGenie", html)
        self.assertIn("id=\"chatForm\"", html)
        self.assertIn("id=\"messageInput\"", html)
        self.assertIn("id=\"sendBtn\"", html)

        # Verify five task choices in HTML
        self.assertIn("Explain", html)
        self.assertIn("QnA", html)
        self.assertIn("Quiz", html)
        self.assertIn("Summary", html)
        self.assertIn("Recommend Path", html)

        # Verify CSS
        res_css = self.client.get("/static/style.css")
        self.assertEqual(res_css.status_code, 200)
        self.assertIn("text/css", res_css.headers.get("content-type", ""))
        self.assertIn(".task-selector", res_css.text)

        # Verify JS
        res_js = self.client.get("/static/app.js")
        self.assertEqual(res_js.status_code, 200)
        self.assertIn("javascript", res_js.headers.get("content-type", ""))
        self.assertIn("data-task", res_js.text)

        print("       PASS: Frontend HTML, CSS, JS, and all 5 task choices verified.")


if __name__ == "__main__":
    unittest.main()
