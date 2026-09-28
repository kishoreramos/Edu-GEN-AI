"""
EduGenie Phase 5A Test Suite: Gemini Model Configuration & Verification
Validates centralized GEMINI_MODEL configuration, absence of gemini-1.5-pro in production code,
module routing through centralized generator, and fallback resilience.
"""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import config
import qna
import explanation_module
import quiz_module
import summary_module
import learning_path

class TestGeminiModelConfiguration(unittest.TestCase):
    def test_01_centralized_model_configured(self):
        """Verify GEMINI_MODEL is centrally configured and exported."""
        self.assertTrue(hasattr(config, "GEMINI_MODEL"))
        self.assertIsInstance(config.GEMINI_MODEL, str)
        self.assertTrue(len(config.GEMINI_MODEL) > 0)
        self.assertNotEqual(config.GEMINI_MODEL, "gemini-1.5-pro")
        print(f"✅ PASS: GEMINI_MODEL is centrally configured to '{config.GEMINI_MODEL}'.")

    def test_02_no_production_code_uses_gemini_1_5_pro(self):
        """Scan all production python files in EduGenie to guarantee no gemini-1.5-pro references."""
        py_files = list(BASE_DIR.glob("*.py")) + list((BASE_DIR / "orchestrator").glob("*.py"))
        found_references = []
        for pf in py_files:
            if pf.name.startswith("test_"):
                continue
            content = pf.read_text(encoding="utf-8", errors="ignore")
            if "gemini-1.5-pro" in content:
                found_references.append(str(pf.name))

        self.assertEqual(found_references, [], f"Found legacy gemini-1.5-pro in: {found_references}")
        print("✅ PASS: Zero occurrences of 'gemini-1.5-pro' in production codebase.")

    def test_03_qa_uses_centralized_model(self):
        """Verify Q&A module routes through generate_gemini_text using centralized model."""
        with patch("qna.generate_gemini_text", return_value="Mocked QA answer") as mock_gen:
            with patch("qna.is_gemini_configured", return_value=True):
                result = qna.answer_question_with_gemini("What is gravity?")
                self.assertEqual(result, "Mocked QA answer")
                mock_gen.assert_called_once()
        print("✅ PASS: Q&A generation uses centralized generate_gemini_text.")

    def test_04_quiz_uses_centralized_model(self):
        """Verify Quiz generation routes through generate_gemini_text using centralized model."""
        sample_quiz_json = '[{"question": "Q1?", "options": ["A", "B", "C", "D"], "answer": "A"}]'
        with patch("quiz_module.generate_gemini_text", return_value=sample_quiz_json) as mock_gen:
            with patch("quiz_module.is_gemini_configured", return_value=True):
                result = quiz_module.generate_quiz("Photosynthesis")
                self.assertIsInstance(result, list)
                self.assertEqual(len(result), 1)
                mock_gen.assert_called_once()
        print("✅ PASS: Quiz generation uses centralized generate_gemini_text.")

    def test_05_summary_uses_centralized_model(self):
        """Verify Summary generation routes through generate_gemini_text using centralized model."""
        with patch("summary_module.generate_gemini_text", return_value="Mocked summary") as mock_gen:
            with patch("summary_module.is_gemini_configured", return_value=True):
                result = summary_module.summarize_text("A long article about thermodynamics...")
                self.assertEqual(result, "Mocked summary")
                mock_gen.assert_called_once()
        print("✅ PASS: Summary generation uses centralized generate_gemini_text.")

    def test_06_learning_path_uses_centralized_model(self):
        """Verify Learning Path generation routes through generate_gemini_text using centralized model."""
        with patch("learning_path.generate_gemini_text", return_value="Mocked roadmap") as mock_gen:
            with patch("learning_path.is_gemini_configured", return_value=True):
                result = learning_path.get_learning_recommendations("Python")
                self.assertEqual(result, "Mocked roadmap")
                mock_gen.assert_called_once()
        print("✅ PASS: Learning path generation uses centralized generate_gemini_text.")

    def test_07_missing_api_key_behavior(self):
        """Verify missing API key handling still produces the documented warning message."""
        with patch("config.is_gemini_configured", return_value=False):
            res = config.generate_gemini_text("Hello")
            self.assertEqual(res, config.GEMINI_KEY_MISSING_ERROR)
        print("✅ PASS: Missing API key returns documented warning message.")

    def test_08_safe_model_status_verification(self):
        """Verify verify_gemini_models_safe utility runs safely without leaking keys."""
        status = config.verify_gemini_models_safe()
        self.assertIsInstance(status, dict)
        self.assertNotIn("GEMINI_API_KEY", status)
        self.assertNotIn("api_key", status)
        print(f"✅ PASS: Model status check returned safely (client_ready: {status.get('client_ready')}).")

if __name__ == "__main__":
    unittest.main()
