"""
EduGenie Baseline Test Suite
Validates all 5 capability modules, input validation, missing API key handling,
and FastAPI endpoint behaviors.
"""
import sys
import unittest
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add EduGenie directory to path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
import main
from qna import answer_question_with_gemini
from explanation_module import explain_topic
from summary_module import summarize_text
from quiz_module import generate_quiz, clean_json_block, validate_quiz_structure
from learning_path import get_learning_recommendations

class TestEduGenieBaseline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    # -------------------------------------------------------------
    # 1. UI Route Test
    # -------------------------------------------------------------
    def test_01_home_page(self):
        """Verify GET / returns 200 and loads HTML template."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Welcome to EduGenie", response.text)
        self.assertIn("Ask EduGenie a Question:", response.text)
        self.assertIn("Need an Explanation?", response.text)
        self.assertIn("Summarize a Paragraph:", response.text)
        self.assertIn("Generate a Quiz:", response.text)
        self.assertIn("Get Learning Recommendations:", response.text)
        print("✅ PASS: Home page loads with all 5 functional sections.")

    # -------------------------------------------------------------
    # 2. Q&A Module & Endpoint Tests
    # -------------------------------------------------------------
    def test_02_qa_empty_input(self):
        """Verify empty input handling in Q&A endpoint and module."""
        res = self.client.get("/qa")
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.json())

        res_space = self.client.get("/qa?question=   ")
        self.assertEqual(res_space.status_code, 400)

        mod_res = answer_question_with_gemini("")
        self.assertIn("⚠️ Error", mod_res)
        print("✅ PASS: Q&A empty input validation returns 400.")

    def test_03_qa_capability(self):
        """Verify Q&A endpoint responds safely (mocked or with missing key notice)."""
        res = self.client.get("/qa?question=What%20is%20the%20largest%20ocean%3F")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("answer", data)
        self.assertTrue(len(data["answer"]) > 0)
        print(f"✅ PASS: Q&A query handled gracefully -> Answer: {data['answer'][:60]}...")

    # -------------------------------------------------------------
    # 3. Explanation Module & Endpoint Tests
    # -------------------------------------------------------------
    def test_04_explain_empty_input(self):
        """Verify explanation rejects empty topic with 400."""
        res = self.client.post("/explain", json={"topic": ""})
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.json())

        res_invalid_json = self.client.post(
            "/explain",
            content="not a json",
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(res_invalid_json.status_code, 400)
        print("✅ PASS: Explanation endpoint validates empty input and invalid JSON.")

    def test_05_explain_capability(self):
        """Verify explanation generates beginner-friendly response or safe notice."""
        res = self.client.post("/explain", json={"topic": "Pythagorean theorem"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["topic"], "Pythagorean theorem")
        self.assertIn("explanation", data)
        self.assertTrue(len(data["explanation"]) > 0)
        print(f"✅ PASS: Explanation handled -> Response: {data['explanation'][:60]}...")

    # -------------------------------------------------------------
    # 4. Summarization Module & Endpoint Tests
    # -------------------------------------------------------------
    def test_06_summarize_empty_input(self):
        """Verify summarization endpoint rejects empty text."""
        res = self.client.post("/summarize", json={"text": "   "})
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.json())
        print("✅ PASS: Summarize empty input validation returns 400.")

    def test_07_summarize_capability(self):
        """Verify text summarization handles educational paragraph."""
        sample_text = (
            "Photosynthesis is the biological process by which green plants and certain other "
            "organisms transform light energy into chemical energy. During photosynthesis in green plants, "
            "light energy is captured and used to convert water, carbon dioxide, and minerals into oxygen "
            "and energy-rich organic compounds."
        )
        res = self.client.post("/summarize", json={"text": sample_text})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("summary", data)
        self.assertTrue(len(data["summary"]) > 0)
        print(f"✅ PASS: Summarize handled -> Response: {data['summary'][:60]}...")

    # -------------------------------------------------------------
    # 5. Quiz Generation Module & Endpoint Tests
    # -------------------------------------------------------------
    def test_08_quiz_empty_input(self):
        """Verify quiz generation rejects empty text."""
        res = self.client.post("/quiz", json={"text": ""})
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.json())
        print("✅ PASS: Quiz empty input validation returns 400.")

    def test_09_quiz_json_parsing_and_structure_validation(self):
        """Verify clean_json_block and validate_quiz_structure on mock AI responses."""
        raw_markdown = """```json
[
  {
    "question": "What does a right triangle have?",
    "options": ["A 90-degree angle", "Three equal sides", "No vertices", "Two hypotenuses"],
    "answer": "A 90-degree angle"
  }
]
```"""
        cleaned = clean_json_block(raw_markdown)
        import json
        parsed = json.loads(cleaned)
        validated = validate_quiz_structure(parsed)
        self.assertEqual(len(validated), 1)
        self.assertEqual(validated[0]["question"], "What does a right triangle have?")
        self.assertEqual(len(validated[0]["options"]), 4)
        self.assertEqual(validated[0]["answer"], "A 90-degree angle")
        print("✅ PASS: Markdown code fence stripping and structure validation work correctly.")

    def test_10_quiz_malformed_ai_handling(self):
        """Verify that malformed JSON from model is caught gracefully without server crash."""
        bad_json = "This is not valid json at all!"
        with self.assertRaises(ValueError):
            validate_quiz_structure(bad_json)
        print("✅ PASS: Malformed AI output caught by validation logic.")

    def test_11_quiz_capability(self):
        """Verify POST /quiz returns list of questions."""
        res = self.client.post("/quiz", json={"text": "Pythagorean Theorem"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("quiz", data)
        self.assertIsInstance(data["quiz"], list)
        self.assertTrue(len(data["quiz"]) > 0)
        print(f"✅ PASS: Quiz endpoint returns {len(data['quiz'])} questions.")

    # -------------------------------------------------------------
    # 6. Learning Path Module & Endpoint Tests
    # -------------------------------------------------------------
    def test_12_learning_path_empty_input(self):
        """Verify learning recommendations rejects empty topic."""
        res = self.client.get("/learn/recommendations")
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.json())
        print("✅ PASS: Learning path empty input returns 400.")

    def test_13_learning_path_capability(self):
        """Verify learning path returns structured recommendation."""
        res = self.client.get("/learn/recommendations?topic=SQL")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["topic"], "SQL")
        self.assertIn("recommendation", data)
        self.assertTrue(len(data["recommendation"]) > 0)
        print(f"✅ PASS: Learning path endpoint handled -> Response: {data['recommendation'][:60]}...")

if __name__ == "__main__":
    unittest.main()
