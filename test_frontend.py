"""
EduGenie Phase 4 - Frontend & Integration Test Suite
Validates unified conversational UI endpoints, session navigation API,
static asset serving, and DOM structure.
"""
import sys
import unittest
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
import main
from orchestrator.session_manager import default_session_manager

class TestEduGenieFrontend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    def test_01_home_page_structure(self):
        """Verify unified conversational layout elements are present on GET /."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.text

        # Core structure
        self.assertIn("EduGenie Learning Companion", html)
        self.assertIn("id=\"messagesContainer\"", html)
        self.assertIn("id=\"welcomeHero\"", html)
        self.assertIn("id=\"chatForm\"", html)
        self.assertIn("id=\"messageInput\"", html)
        self.assertIn("id=\"sendBtn\"", html)
        self.assertIn("id=\"sessionList\"", html)
        self.assertIn("id=\"newChatBtn\"", html)
        self.assertIn("id=\"typingIndicator\"", html)
        print("✅ PASS: Home page contains unified conversational interface elements.")

    def test_02_static_assets_served(self):
        """Verify static CSS and JS are served correctly."""
        res_css = self.client.get("/static/style.css")
        self.assertEqual(res_css.status_code, 200)
        self.assertIn("text/css", res_css.headers.get("content-type", ""))
        self.assertIn(".app-layout", res_css.text)

        res_js = self.client.get("/static/app.js")
        self.assertEqual(res_js.status_code, 200)
        self.assertIn("javascript", res_js.headers.get("content-type", ""))
        self.assertIn("buildQuizWidget", res_js.text)
        print("✅ PASS: Static CSS and JavaScript served with correct content-types.")

    def test_03_get_all_sessions_api(self):
        """Verify GET /api/sessions returns list of sessions with titles and message counts."""
        # Create a session with a message first
        sess_id = default_session_manager.create_session()
        default_session_manager.add_message(sess_id, "user", "Explain how binary search works")
        default_session_manager.add_message(sess_id, "assistant", "Binary search is an efficient algorithm...")

        res = self.client.get("/api/sessions?limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("sessions", data)
        self.assertIsInstance(data["sessions"], list)

        # Check our session is in the list
        matching = [s for s in data["sessions"] if s["session_id"] == sess_id]
        self.assertTrue(len(matching) > 0)
        sess_meta = matching[0]
        self.assertIn("title", sess_meta)
        self.assertIn("message_count", sess_meta)
        self.assertGreaterEqual(sess_meta["message_count"], 2)
        print(f"✅ PASS: GET /api/sessions returned session metadata (Title: '{sess_meta['title']}', msgs: {sess_meta['message_count']}).")

    def test_04_session_history_api(self):
        """Verify GET /api/session/{id}/history returns messages."""
        sess_id = default_session_manager.create_session()
        default_session_manager.add_message(sess_id, "user", "What is an API?")
        default_session_manager.add_message(sess_id, "assistant", "An API stands for Application Programming Interface.")

        res = self.client.get(f"/api/session/{sess_id}/history?limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["session_id"], sess_id)
        self.assertEqual(len(data["messages"]), 2)
        self.assertEqual(data["messages"][0]["content"], "What is an API?")
        print("✅ PASS: GET /api/session/{id}/history retrieved full message history.")

if __name__ == "__main__":
    unittest.main()
