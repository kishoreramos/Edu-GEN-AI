"""
EduGenie Phase 2 Test Suite: Intent Classification, Tool Router, and Workflow Engine
Validates all required queries, intent categories, module tool invocations,
multi-action workflows, context requirements, and the POST /api/chat endpoint.
"""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
import main
from orchestrator.schemas import IntentType, StructuredIntent, ActionItem
from orchestrator.intent_classifier import classify_intent
from orchestrator.router import route_intent, process_message
from orchestrator.workflow import execute_multi_action_workflow

class TestEduGenieOrchestrator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    # -------------------------------------------------------------
    # 1. Minimum Required Intent Classification Tests
    # -------------------------------------------------------------
    def test_01_intent_qa(self):
        """Query 1: 'What is the largest ocean?' -> QA"""
        intent = classify_intent("What is the largest ocean?")
        self.assertEqual(intent.intent, IntentType.QA)
        print(f"✅ PASS [Intent QA]: 'What is the largest ocean?' -> {intent.intent}")

    def test_02_intent_explain(self):
        """Query 2: 'Explain recursion in simple terms.' -> EXPLAIN"""
        intent = classify_intent("Explain recursion in simple terms.")
        self.assertEqual(intent.intent, IntentType.EXPLAIN)
        print(f"✅ PASS [Intent EXPLAIN]: 'Explain recursion in simple terms.' -> {intent.intent}")

    def test_03_intent_quiz(self):
        """Query 3: 'Test me on recursion.' -> QUIZ"""
        intent = classify_intent("Test me on recursion.")
        self.assertEqual(intent.intent, IntentType.QUIZ)
        print(f"✅ PASS [Intent QUIZ]: 'Test me on recursion.' -> {intent.intent}")

    def test_04_intent_summarize(self):
        """Query 4: 'Summarize this paragraph.' -> SUMMARIZE"""
        intent = classify_intent("Summarize this paragraph: Photosynthesis is the process by which green plants make food.")
        self.assertEqual(intent.intent, IntentType.SUMMARIZE)
        print(f"✅ PASS [Intent SUMMARIZE]: 'Summarize this paragraph.' -> {intent.intent}")

    def test_05_intent_learning_path(self):
        """Query 5: 'Give me a roadmap to learn SQL.' -> LEARNING_PATH"""
        intent = classify_intent("Give me a roadmap to learn SQL.")
        self.assertEqual(intent.intent, IntentType.LEARNING_PATH)
        print(f"✅ PASS [Intent LEARNING_PATH]: 'Give me a roadmap to learn SQL.' -> {intent.intent}")

    def test_06_intent_multi_action_summary_quiz(self):
        """Query 6: 'Summarize this text and then quiz me.' -> MULTI_ACTION"""
        intent = classify_intent("Summarize this text and then quiz me.")
        self.assertEqual(intent.intent, IntentType.MULTI_ACTION)
        self.assertGreaterEqual(len(intent.actions), 2)
        self.assertEqual(intent.actions[0].intent, IntentType.SUMMARIZE)
        self.assertEqual(intent.actions[1].intent, IntentType.QUIZ)
        self.assertEqual(intent.actions[1].depends_on, "previous_result")
        print(f"✅ PASS [Intent MULTI_ACTION 1]: Summarize then quiz -> {intent.intent}")

    def test_07_intent_multi_action_explain_quiz(self):
        """Query 7: 'Explain photosynthesis and then test me.' -> MULTI_ACTION"""
        intent = classify_intent("Explain photosynthesis and then test me.")
        self.assertEqual(intent.intent, IntentType.MULTI_ACTION)
        self.assertGreaterEqual(len(intent.actions), 2)
        self.assertEqual(intent.actions[0].intent, IntentType.EXPLAIN)
        self.assertEqual(intent.actions[1].intent, IntentType.QUIZ)
        print(f"✅ PASS [Intent MULTI_ACTION 2]: Explain then test -> {intent.intent}")

    def test_08_intent_clarification(self):
        """Query 8: 'Tell me more about Python.' -> CLARIFICATION"""
        intent = classify_intent("Tell me more about Python.")
        self.assertEqual(intent.intent, IntentType.CLARIFICATION)
        self.assertIsNotNone(intent.clarification_prompt)
        print(f"✅ PASS [Intent CLARIFICATION]: 'Tell me more about Python.' -> {intent.intent}")

    def test_09_intent_greeting_unknown(self):
        """Query 9: 'Hello EduGenie.' -> UNKNOWN (Greeting)"""
        intent = classify_intent("Hello EduGenie.")
        self.assertEqual(intent.intent, IntentType.UNKNOWN)
        print(f"✅ PASS [Intent GREETING]: 'Hello EduGenie.' -> {intent.intent}")

    def test_10_intent_offtopic_unknown(self):
        """Query 10: 'Do something random.' -> UNKNOWN"""
        intent = classify_intent("Do something random.")
        self.assertEqual(intent.intent, IntentType.UNKNOWN)
        print(f"✅ PASS [Intent UNKNOWN]: 'Do something random.' -> {intent.intent}")

    # -------------------------------------------------------------
    # 2. Context Dependency Tests
    # -------------------------------------------------------------
    def test_11_context_dependent_queries(self):
        """Queries relying on missing context flag requires_context and ask for clarification."""
        q1 = classify_intent("Explain that more simply.")
        self.assertEqual(q1.intent, IntentType.CLARIFICATION)
        self.assertTrue(q1.requires_context)

        q2 = classify_intent("Quiz me on that.")
        self.assertEqual(q2.intent, IntentType.CLARIFICATION)
        self.assertTrue(q2.requires_context)
        print("✅ PASS [Context Dependent]: Missing context flagged as CLARIFICATION (requires_context=True).")

    # -------------------------------------------------------------
    # 3. Tool Routing Tests (Verifying Underlying Modules Are Called)
    # -------------------------------------------------------------
    @patch("orchestrator.router.answer_question_with_gemini")
    def test_12_route_qa_calls_qna_module(self, mock_qa):
        mock_qa.return_value = "Mocked Pacific Ocean answer."
        intent = StructuredIntent(intent=IntentType.QA, topic="What is the largest ocean?")
        res = route_intent(intent, "What is the largest ocean?")
        mock_qa.assert_called_once_with("What is the largest ocean?")
        self.assertEqual(res.tool, "QA")
        self.assertEqual(res.content, "Mocked Pacific Ocean answer.")
        print("✅ PASS [Router Tool Invocation]: QA intent successfully invokes qna.py.")

    @patch("orchestrator.router.explain_topic")
    def test_13_route_explain_calls_explanation_module(self, mock_explain):
        mock_explain.return_value = "Mocked simplified recursion explanation."
        intent = StructuredIntent(intent=IntentType.EXPLAIN, topic="recursion")
        res = route_intent(intent, "Explain recursion simply")
        mock_explain.assert_called_once_with("recursion")
        self.assertEqual(res.tool, "EXPLAIN")
        self.assertEqual(res.content, "Mocked simplified recursion explanation.")
        print("✅ PASS [Router Tool Invocation]: EXPLAIN intent successfully invokes explanation_module.py.")

    @patch("orchestrator.router.generate_quiz")
    def test_14_route_quiz_calls_quiz_module(self, mock_quiz):
        mock_quiz.return_value = [
            {"question": "Q1?", "options": ["A", "B", "C", "D"], "answer": "A"}
        ]
        intent = StructuredIntent(intent=IntentType.QUIZ, topic="recursion", question_count=3)
        res = route_intent(intent, "Test me on recursion")
        mock_quiz.assert_called_once_with("recursion")
        self.assertEqual(res.tool, "QUIZ")
        self.assertEqual(len(res.data["quiz"]), 1)
        print("✅ PASS [Router Tool Invocation]: QUIZ intent successfully invokes quiz_module.py.")

    @patch("orchestrator.router.summarize_text")
    def test_15_route_summary_calls_summary_module(self, mock_summary):
        mock_summary.return_value = "Mocked short summary."
        intent = StructuredIntent(intent=IntentType.SUMMARIZE, input_text="Long passage text here")
        res = route_intent(intent, "Summarize this paragraph")
        mock_summary.assert_called_once_with("Long passage text here")
        self.assertEqual(res.tool, "SUMMARIZE")
        self.assertEqual(res.content, "Mocked short summary.")
        print("✅ PASS [Router Tool Invocation]: SUMMARIZE intent successfully invokes summary_module.py.")

    @patch("orchestrator.router.get_learning_recommendations")
    def test_16_route_learning_path_calls_learning_path_module(self, mock_path):
        mock_path.return_value = "Mocked SQL Roadmap from Beginner to Advanced."
        intent = StructuredIntent(intent=IntentType.LEARNING_PATH, topic="SQL")
        res = route_intent(intent, "Give me a roadmap to learn SQL")
        mock_path.assert_called_once_with("SQL")
        self.assertEqual(res.tool, "LEARNING_PATH")
        self.assertEqual(res.content, "Mocked SQL Roadmap from Beginner to Advanced.")
        print("✅ PASS [Router Tool Invocation]: LEARNING_PATH intent successfully invokes learning_path.py.")

    # -------------------------------------------------------------
    # 4. Multi-Action Workflow Sequential Pipeline Test
    # -------------------------------------------------------------
    @patch("orchestrator.workflow.summarize_text")
    @patch("orchestrator.workflow.generate_quiz")
    def test_17_multi_action_workflow_execution(self, mock_quiz, mock_summary):
        mock_summary.return_value = "Condensed text summary regarding Photosynthesis."
        mock_quiz.return_value = [
            {"question": "What is produced in photosynthesis?", "options": ["Oxygen", "Carbon", "Nitrogen", "Iron"], "answer": "Oxygen"}
        ]

        intent = StructuredIntent(
            intent=IntentType.MULTI_ACTION,
            actions=[
                ActionItem(intent=IntentType.SUMMARIZE, input_text="Raw long paragraph"),
                ActionItem(intent=IntentType.QUIZ, depends_on="previous_result")
            ]
        )

        res = execute_multi_action_workflow(intent, "Summarize this text and then quiz me.")
        self.assertTrue(res.success)
        self.assertEqual(res.tool, "MULTI_ACTION")
        self.assertEqual(len(res.data["steps"]), 2)
        # Check that quiz received the output of the summary!
        mock_summary.assert_called_once_with("Raw long paragraph")
        mock_quiz.assert_called_once_with("Condensed text summary regarding Photosynthesis.")
        print("✅ PASS [Multi-Action Pipeline]: Action 2 successfully consumed Action 1 result.")

    # -------------------------------------------------------------
    # 5. POST /api/chat HTTP API Tests
    # -------------------------------------------------------------
    def test_18_chat_api_empty_message(self):
        """POST /api/chat with empty message returns 400 Bad Request."""
        res = self.client.post("/api/chat", json={"message": "   "})
        self.assertEqual(res.status_code, 400)
        print("✅ PASS [API /api/chat]: Empty message rejected with 400.")

    def test_19_chat_api_successful_turn(self):
        """POST /api/chat with question returns structured ChatResponse."""
        res = self.client.post("/api/chat", json={"message": "What is the largest ocean?"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["intent"], "QA")
        self.assertIn("reply", data)
        self.assertIn("data", data)
        print("✅ PASS [API /api/chat]: Valid message processed into structured ChatResponse.")

    def test_20_chat_api_greeting_no_tool(self):
        """POST /api/chat with greeting returns friendly message without invoking tool."""
        res = self.client.post("/api/chat", json={"message": "Hello EduGenie"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["intent"], "UNKNOWN")
        self.assertIn("personal AI learning assistant", data["reply"])
        print("✅ PASS [API /api/chat]: Greeting returned conversational response without tool invocation.")

if __name__ == "__main__":
    unittest.main()
