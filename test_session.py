"""
EduGenie Phase 3 Test Suite: Session State & Conversation Engine
Validates all 13 required session test scenarios: automatic session creation,
history tracking, contextual topic resolution, active quiz tracking, bounded history,
server restart persistence, unknown session handling, and missing context handling.
"""
import os
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
from orchestrator.schemas import IntentType, ContextState, QuizState
from orchestrator.session_manager import SessionManager, default_session_manager

class TestEduGenieSessionEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)
        cls.sm = default_session_manager

    # -------------------------------------------------------------
    # TEST 1 & 2: Automatic Session Creation & Return session_id
    # -------------------------------------------------------------
    def test_01_create_session_automatically_and_return_id(self):
        """TEST 1 & 2: Automatically create session and return session_id on /api/chat."""
        res = self.client.post("/api/chat", json={"message": "What is Python?"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("session_id", data)
        self.assertIsNotNone(data["session_id"])
        self.assertTrue(len(data["session_id"]) > 0)
        print(f"✅ PASS [TEST 1 & 2]: Session created automatically -> session_id: {data['session_id']}")

    # -------------------------------------------------------------
    # TEST 3, 4 & 5: Store User Message, Assistant Reply, & Retrieve History
    # -------------------------------------------------------------
    def test_02_store_and_retrieve_messages(self):
        """TEST 3, 4 & 5: Store user and assistant messages and retrieve bounded history."""
        session_id = self.sm.create_session()
        self.sm.add_message(session_id, role="user", content="Hello EduGenie", intent="UNKNOWN")
        self.sm.add_message(session_id, role="assistant", content="Hello! How can I help you?", intent="UNKNOWN")

        history = self.sm.get_recent_messages(session_id, limit=10)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].role, "user")
        self.assertEqual(history[0].content, "Hello EduGenie")
        self.assertEqual(history[1].role, "assistant")
        self.assertEqual(history[1].content, "Hello! How can I help you?")

        # Test via HTTP API
        res = self.client.get(f"/api/session/{session_id}/history")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()["messages"]), 2)
        print("✅ PASS [TEST 3, 4 & 5]: Messages stored and retrieved accurately.")

    # -------------------------------------------------------------
    # TEST 6: Remember Current Topic ("What is recursion?" -> "Explain it more simply.")
    # -------------------------------------------------------------
    def test_03_remember_current_topic_simplification(self):
        """TEST 6: Multi-turn context resolution: 'What is recursion?' followed by 'Explain it more simply.'"""
        # Turn 1: Ask about recursion
        res1 = self.client.post("/api/chat", json={"message": "What is recursion?"})
        self.assertEqual(res1.status_code, 200)
        sid = res1.json()["session_id"]

        # Turn 2: Follow-up using anaphora 'it'
        res2 = self.client.post("/api/chat", json={"session_id": sid, "message": "Explain it more simply."})
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data2["intent"], "EXPLAIN")
        self.assertIn("recursion", str(data2["data"].get("topic", "")).lower())
        print("✅ PASS [TEST 6]: Follow-up 'Explain it more simply' resolved topic to 'recursion'.")

    # -------------------------------------------------------------
    # TEST 7: Contextual Quiz ("What is inheritance?" -> "Quiz me.")
    # -------------------------------------------------------------
    def test_04_contextual_quiz_generation(self):
        """TEST 7: Multi-turn context resolution: 'What is inheritance?' followed by 'Quiz me.'"""
        # Turn 1: Establish topic
        res1 = self.client.post("/api/chat", json={"message": "What is inheritance in Java?"})
        self.assertEqual(res1.status_code, 200)
        sid = res1.json()["session_id"]

        # Turn 2: Request quiz on active topic
        res2 = self.client.post("/api/chat", json={"session_id": sid, "message": "Now quiz me."})
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data2["intent"], "QUIZ")
        self.assertIn("inheritance", str(data2["data"].get("topic", "")).lower())
        print("✅ PASS [TEST 7]: Follow-up 'Now quiz me' resolved topic to 'inheritance'.")

    # -------------------------------------------------------------
    # TEST 8: Active Quiz State & Feedback ("I got 2 wrong.")
    # -------------------------------------------------------------
    def test_05_active_quiz_feedback(self):
        """TEST 8: Turn 1 generates quiz; Turn 2 'I got 2 wrong.' updates quiz score and gives feedback."""
        # Turn 1: Generate quiz
        res1 = self.client.post("/api/chat", json={"message": "Generate a quiz about the solar system."})
        self.assertEqual(res1.status_code, 200)
        sid = res1.json()["session_id"]

        # Turn 2: Report score
        res2 = self.client.post("/api/chat", json={"session_id": sid, "message": "I got 2 wrong."})
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data2["intent"], "QUIZ")
        self.assertTrue(data2["data"].get("quiz_feedback"))
        self.assertEqual(data2["data"].get("score"), 1)  # 3 total - 2 wrong = 1
        print("✅ PASS [TEST 8]: 'I got 2 wrong' evaluated against active quiz (Score: 1/3).")

    # -------------------------------------------------------------
    # TEST 9: Next Step Recommendations ("What should I learn next?")
    # -------------------------------------------------------------
    def test_06_contextual_learning_path_next_steps(self):
        """TEST 9: Turn 1 'What is inheritance?' followed by Turn 2 'What should I learn next?'"""
        # Turn 1: Topic
        res1 = self.client.post("/api/chat", json={"message": "What is inheritance?"})
        sid = res1.json()["session_id"]

        # Turn 2: Next steps
        res2 = self.client.post("/api/chat", json={"session_id": sid, "message": "What should I learn next?"})
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data2["intent"], "LEARNING_PATH")
        self.assertIn("inheritance", str(data2["data"].get("topic", "")).lower())
        print("✅ PASS [TEST 9]: 'What should I learn next?' contextualized with previous topic.")

    # -------------------------------------------------------------
    # TEST 10: Bounded History Truncation
    # -------------------------------------------------------------
    def test_07_bounded_history_truncation(self):
        """TEST 10: Verify history is strictly bounded (does not exceed limit)."""
        sid = self.sm.create_session()
        # Add 15 messages
        for i in range(15):
            self.sm.add_message(sid, role="user" if i % 2 == 0 else "assistant", content=f"Message {i}")

        bounded = self.sm.get_recent_messages(sid, limit=10)
        self.assertEqual(len(bounded), 10)
        # Oldest of the 10 should be Message 5, newest should be Message 14
        self.assertEqual(bounded[0].content, "Message 5")
        self.assertEqual(bounded[-1].content, "Message 14")
        print("✅ PASS [TEST 10]: History bounded to 10 messages; older messages truncated.")

    # -------------------------------------------------------------
    # TEST 11: Server Restart Persistence (SQLite State Survives Reload)
    # -------------------------------------------------------------
    def test_08_server_restart_persistence(self):
        """TEST 11: Create state with SessionManager 1, discard, create SessionManager 2, verify state persists."""
        restart_db = BASE_DIR / "restart_test.db"
        sm1 = SessionManager(db_path=str(restart_test_db := restart_db))
        sid = sm1.create_session()
        ctx = ContextState(current_topic="Quantum Computing", recent_topics=["Quantum Computing"])
        sm1.update_session_context(sid, ctx)
        sm1.add_message(sid, role="user", content="Explain quantum computing")
        sm1.add_message(sid, role="assistant", content="Quantum computing uses qubits...")
        del sm1

        # Simulate complete restart by instantiating new SessionManager pointing to same SQLite file
        sm2 = SessionManager(db_path=str(restart_test_db))
        recovered_id, recovered_ctx = sm2.get_or_create_session(sid)
        recovered_msgs = sm2.get_recent_messages(sid)
        del sm2

        # Clean up test file
        try:
            if restart_db.exists():
                restart_db.unlink()
        except Exception:
            pass

        self.assertEqual(recovered_id, sid)
        self.assertEqual(recovered_ctx.current_topic, "Quantum Computing")
        self.assertEqual(len(recovered_msgs), 2)
        print("✅ PASS [TEST 11]: Session state and messages persisted across simulated restart.")

    # -------------------------------------------------------------
    # TEST 12: Unknown / Malformed Session ID Handling
    # -------------------------------------------------------------
    def test_09_unknown_or_malformed_session_handling(self):
        """TEST 12: Passing non-existent or invalid session_id creates new valid session gracefully."""
        # Non-existent ID
        res1 = self.client.post("/api/chat", json={"session_id": "non_existent_123", "message": "What is Python?"})
        self.assertEqual(res1.status_code, 200)
        self.assertTrue(res1.json()["success"])

        # Malformed ID with invalid characters
        res2 = self.client.post("/api/chat", json={"session_id": "bad;DROP TABLE--", "message": "What is Python?"})
        self.assertEqual(res2.status_code, 200)
        self.assertTrue(res2.json()["success"])
        # Should sanitize/generate clean session_id
        clean_sid = res2.json()["session_id"]
        self.assertNotIn(";", clean_sid)
        print("✅ PASS [TEST 12]: Unknown and malformed session IDs handled safely.")

    # -------------------------------------------------------------
    # TEST 13: Missing Context Resolution (Zero Hallucination)
    # -------------------------------------------------------------
    def test_10_missing_context_clarification(self):
        """TEST 13: 'Explain that again.' in an empty session flags CLARIFICATION without hallucination."""
        # Create fresh session with no prior topic
        res_new = self.client.post("/api/session")
        sid = res_new.json()["session_id"]

        res = self.client.post("/api/chat", json={"session_id": sid, "message": "Explain that again."})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["intent"], "CLARIFICATION")
        self.assertTrue(data["data"].get("requires_context"))
        self.assertIn("specify which topic", data["reply"])
        print("✅ PASS [TEST 13]: Missing context flagged as CLARIFICATION (no hallucination).")

if __name__ == "__main__":
    unittest.main()
