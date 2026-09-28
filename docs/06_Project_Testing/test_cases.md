# Phase 6: Project Testing Phase — Detailed Test Cases
## Project: EduGenie — Google Gemini Powered Learning Assistant

---

### Standard Test Case Specification

| Test ID | Feature | Input / Precondition | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-001** | Academic Q&A | Input: *"What is polymorphism in Java?"* submitted via `qna.py` and `POST /qa` | Returns factual, accurate explanation of Java polymorphism (>20 chars). Rejects empty input with HTTP 400. | Generated detailed response explaining method overloading and overriding. Empty input returned 400. | **PASS** |
| **TC-002** | Concept Explanation | Input: *"Recursion in Java"* submitted via `explanation_module.py` and `POST /explain` | Returns beginner-friendly explanation with real-world analogy. Falls back to Gemini if local model absent. | Generated structured explanation using Russian doll analogy. Fallback triggered seamlessly. | **PASS** |
| **TC-003** | Quiz Generation | Input: *"Pythagorean Theorem"* submitted via `quiz_module.py` and `POST /quiz` | Returns JSON array of exactly 3 questions, each having 4 options and valid answer key. | Returned 3 valid MCQs with 4 options each and correct answer keys. | **PASS** |
| **TC-004** | Text Summarization | Input: Paragraph describing the Industrial Revolution submitted via `POST /summarize` | Returns bulleted key takeaways and a concise 3-sentence summary. | Output properly organized into Key Takeaways and 3-Sentence Summary. | **PASS** |
| **TC-005** | Learning Path | Input: *"Python Programming"* submitted via `POST /learn/recommendations` | Returns sequential roadmap categorized into Beginner, Intermediate, and Advanced milestones. | Generated structured roadmap covering syntax, OOP, and advanced concepts. | **PASS** |
| **TC-006** | Original API Endpoints | Direct HTTP POST calls to `/qa`, `/explain`, `/quiz`, `/summarize`, and `/learn/recommendations` | All endpoints return HTTP 200 with valid schema payloads; empty payloads return HTTP 400. | All 5 direct endpoints returned valid 200 responses and 400 error codes on empty inputs. | **PASS** |
| **TC-007** | Frontend Task Selection | Clicking task chips (`Auto`, `Explain`, `Q&A`, `Quiz`, `Summary`, `Learning Path`) | Active pill updates state; sends `task_override` parameter in `/api/chat` payload. | Selected chip receives `.active` class; subsequent prompt dispatches with manual override. | **PASS** |
| **TC-008** | Auto Intent Routing | User enters: *"Quiz me on machine learning"* in Auto mode via `POST /api/chat` | Router classifies prompt as `QUIZ` and dispatches to quiz module without manual selection. | Intent resolved as `QUIZ` in $< 5\text{ ms}$; returned interactive quiz widget. | **PASS** |
| **TC-009** | Contextual Follow-Up | Turn 1: *"What is photosynthesis?"*<br>Turn 2: *"Can you explain that more simply?"* | Turn 2 resolves *"that"* as Photosynthesis and calls explanation module. | Correctly identified Photosynthesis as active topic and simplified the concept. | **PASS** |
| **TC-010** | Quiz Contextual Behavior | Active quiz present; user enters: *"1 is A, 2 is C, 3 is B"* | System intercepts submission, evaluates answers against stored quiz, and returns score with feedback. | Scored answers, updated session score in SQLite, and flagged incorrect questions for review. | **PASS** |
| **TC-011** | UI Browser Rendering | Navigate to `http://127.0.0.1:8000` on desktop browser | Home state renders centered hero, sparkle logo, composer dock, and ambient Canvas background. | Screen rendered centered layout, responsive input box, and glowing brand sparkle cleanly. | **PASS** |
| **TC-012** | Responsive / Mobile Behavior | Viewport resized to mobile (390x844px) | Composer chips wrap cleanly; Lightfall streak density scales down; zero horizontal scrollbar. | Layout adapted cleanly without clipping; Lightfall density reduced by 55% for battery saving. | **PASS** |
| **TC-013** | Lightfall Background Visuals | Canvas 2D engine initializes on `#lightfallCanvas` | Renders curved diagonal trails (~26°), 3-tier depth, bright tips, and auto-dims in chat mode. | Verified via browser screenshot: continuous light rain cascade, ambient celestial bloom, dimming on chat. | **PASS** |
