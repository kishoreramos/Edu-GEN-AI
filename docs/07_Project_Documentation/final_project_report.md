# Final Project Report
# EDUGENIE — GOOGLE GEMINI POWERED LEARNING ASSISTANT

---

## 1. Abstract
**EduGenie** is an intelligent, AI-native educational learning assistant developed to empower students and self-directed learners with on-demand academic tutoring. By harnessing the language comprehension capabilities of Google Gemini through modern FastAPI architecture, EduGenie unifies five foundational pedagogical services: academic question answering, simplified concept explanations with analogies, interactive multiple-choice quiz generation, educational text summarization, and structured multi-tier learning paths. Built with an intelligent orchestration layer supporting 0ms fast intent classification, multi-turn conversational context resolution, persistent SQLite session memory, and an interactive GPU-accelerated Canvas background ("Lightfall"), EduGenie bridges the divide between passive studying and active, personalized learning.

---

## 2. Introduction
In modern educational ecosystems, students are frequently faced with vast amounts of uncurated information. Digital textbooks, online repositories, and reference websites offer comprehensive raw material, yet they lack the adaptive pedagogical scaffolding of a human tutor. When self-directed learners encounter complex, abstract concepts—ranging from computer science data structures to calculus—they often struggle with cognitive fatigue and disengagement. EduGenie addresses this challenge by providing an accessible, responsive, and pedagogically sound assistant capable of explaining difficult topics in simple terms, validating knowledge through active recall testing, and generating sequential roadmaps to guide student progression.

---

## 3. Problem Statement
Learners across secondary, higher, and independent educational paths encounter persistent barriers:
1. **Dense and Verbose Textbooks:** Technical explanations often assume prerequisite context that beginners do not possess.
2. **Fragmented Learning Toolsets:** Students toggle between search engines, summarizers, flashcard generators, and roadmap blogs, breaking study momentum.
3. **Absence of Immediate Knowledge Verification:** Passive reading fails to reinforce retention. Students rarely test themselves immediately after reading new material.
4. **Context Blindness in Conventional Tools:** Most AI utilities operate statelessly, forcing students to retype context whenever asking follow-up questions.

---

## 4. Objectives
- **Core Pedagogical Objectives:**
  - Provide accurate, factually grounded academic answers to direct inquiries.
  - Deconstruct complex topics using relatable everyday analogies and simplified vocabulary.
  - Implement active recall via 3-question multiple-choice quizzes with instant grading.
  - Summarize verbose texts into key takeaways and concise summaries.
  - Formulate structured 3-tiered learning paths (Beginner, Intermediate, Advanced).
- **Technical & Architectural Objectives:**
  - Build an asynchronous, modular backend leveraging FastAPI and Python 3.12.
  - Provide resilient Gemini SDK integration with automated model fallback chains.
  - Retain 100% backwards compatibility with all five original documented REST endpoints.
  - Implement multi-turn conversational memory persisted via an embedded SQLite database.
  - Deliver a zero-dependency, lightweight, responsive web interface featuring ambient GPU-accelerated visuals.

---

## 5. Existing System
Traditional online educational aids typically present severe constraints:
- **Static Quiz Banks:** Questions are pre-compiled, rigid, and disconnected from the exact topic the student is studying.
- **Search Engines:** Return millions of unstructured links requiring extensive manual synthesis.
- **Generic Chatbots:** Often output excessively verbose or hallucinated responses without educational structure, lack dedicated quiz evaluation mechanisms, and lack level-specific learning roadmaps.

---

## 6. Proposed System
EduGenie introduces a structured educational workspace combining dedicated capability modules with conversational intelligence:
- **Unified Single-Box Interaction:** Students can type naturally or select dedicated capability chips (`Auto`, `Explain`, `Q&A`, `Quiz`, `Summary`, `Learning Path`).
- **Pedagogical Prompt Engineering:** Prompts are specifically tuned for clarity, analogies, and structured formatting rather than generic conversational filler.
- **Dual Routing Pipeline:** Fast regex pre-routing resolves explicit educational intents instantly ($< 1\text{ ms}$), with Gemini handling complex conversational queries.
- **Stateful Learning Context:** The system remembers the topic under discussion, allowing fluid multi-turn tutoring.

---

## 7. Functional Requirements
- **FR-01 (Q&A):** Answer direct academic queries accurately via Google Gemini.
- **FR-02 (Explanation):** Provide simplified conceptual explanations with real-world analogies (with local LaMini sequence model fallback).
- **FR-03 (Quiz Generation):** Produce structured 3-question MCQs with 4 options and valid answer keys.
- **FR-04 (Summarization):** Distill passages into bulleted takeaways and a 3-sentence summary.
- **FR-05 (Learning Path):** Generate sequential Beginner, Intermediate, and Advanced milestones.
- **FR-06 (Direct Endpoints):** Provide programmatic access via `/qa`, `/explain`, `/quiz`, `/summarize`, `/learn/recommendations`.
- **FR-07 (Conversational Orchestration):** Accept multi-turn queries at `POST /api/chat`, classify intent, and dispatch tools.
- **FR-08 (Persistence):** Store messages, sessions, and quiz evaluations in an embedded SQLite database.
- **FR-09 (Interactive Frontend):** Render Markdown, clickable quiz cards with immediate grading, and suggestion chips.

---

## 8. Non-Functional Requirements
- **NFR-01 (Performance):** Zero-latency local intent classification ($< 1\text{ ms}$) and bounded response timeouts ($< 10\text{ s}$).
- **NFR-02 (Reliability):** Automated Gemini model fallback (`gemini-2.5-flash` $\rightarrow$ `gemma-4-26b-a4b-it`) preventing API downtime.
- **NFR-03 (Security):** Strict credential isolation via `.env`, parameter binding in SQLite, and zero API key exposure.
- **NFR-04 (Portability):** Pure Python backend and zero-build vanilla HTML/CSS/JS frontend.
- **NFR-05 (Accessibility):** Full mobile responsiveness and `prefers-reduced-motion` compliance.

---

## 9. System Architecture
EduGenie follows a multi-tiered architecture:
1. **Presentation Layer:** Vanilla HTML5/CSS3/ES6 running in browser with Canvas 2D ambient Lightfall graphics.
2. **API Routing Layer:** FastAPI application exposing direct endpoints and conversational orchestrator.
3. **Orchestration Layer:** Fast local keyword pre-router, Gemini classifier, and context engine.
4. **Core Capability Modules:** Five decoupled Python modules (`qna`, `explanation_module`, `quiz_module`, `summary_module`, `learning_path`).
5. **AI Inference Layer:** Google Gemini API with centralized fallback.
6. **Persistence Layer:** Embedded SQLite 3 database (`edugenie.db`).

---

## 10. Technology Stack
- **Backend:** Python 3.12, FastAPI 0.110+, Uvicorn 0.28+, Pydantic v2, Jinja2.
- **AI / LLM:** Google Gemini (`google-genai` and `google-generativeai`).
- **Database:** SQLite 3.
- **Frontend:** HTML5, CSS3 (Custom Variables, Flexbox/Grid), JavaScript (ES6+), HTML5 Canvas 2D.
- **Testing:** Python `unittest`, FastAPI `TestClient`, Microsoft Edge Headless.

---

## 11. Module Description
- **`qna.py`:** Generates structured, verified academic answers.
- **`explanation_module.py`:** Delivers structured concept breakdowns with analogies; integrates local model pipeline with automatic Gemini fallback.
- **`quiz_module.py`:** Prompts Gemini for JSON-formatted quizzes; parses, sanitizes, and validates 4-option MCQs.
- **`summary_module.py`:** Formulates educational summaries divided into Key Takeaways and 3-Sentence Summaries.
- **`learning_path.py`:** Constructs progressive 3-tier learning roadmaps.

---

## 12. API Description
- `POST /qa`: Direct academic question answering.
- `POST /explain`: Simplified concept explanations.
- `POST /quiz`: 3-question MCQ quiz generation.
- `POST /summarize`: Text summarization.
- `POST /learn/recommendations`: Structured learning path generation.
- `POST /api/chat`: Multi-turn conversational tutor orchestrating educational tools.
- `POST /api/session`: Explicit session initialization.
- `GET /api/session/{session_id}/history`: Retrieval of recent session message turns.
- `GET /api/sessions`: Listing of recent conversation sessions.

---

## 13. Database/Session Design
Managed via `orchestrator/session_manager.py` using SQLite:
- `sessions`: Stores `session_id`, `created_at`, `updated_at`, `current_topic`, `context_json`, `summary`.
- `messages`: Stores individual user/assistant turns linked to sessions with `ON DELETE CASCADE`.
- `quiz_sessions`: Tracks generated quizzes, questions, options, user score, and identified weak areas.

---

## 14. User Interface
- **Home State:** Clean, focused hero section with glowing brand sparkle (`✦`), typography, and docked composer accompanied by task selection chips.
- **Chat State:** Seamlessly expands into an interactive conversational stream with formatted Markdown, code syntax styling, clickable quiz option cards, and contextual suggestion chips.
- **Ambient Lightfall Visuals:** Canvas 2D background rendering continuous curved diagonal ribbons with 3-tier perspective depth, upper celestial bloom, and pointer reactivity.

---

## 15. Intelligent Intent Routing
Implements a two-tiered classification pipeline:
1. **Tier 1 (Fast Regex Pre-Router):** Immediately identifies clear command keywords (`"quiz"`, `"explain"`, `"summarize"`, `"path"`) in $< 1\text{ ms}$ with zero API calls.
2. **Tier 2 (Gemini Few-Shot Classifier):** Handles complex, multi-sentence conversational queries to classify intent accurately.

---

## 16. Core Workflow
1. User enters query in the composer.
2. If in `Auto` mode, pre-router/classifier determines the pedagogical intent.
3. Context engine checks session history to resolve pronouns (*"explain that"*, *"quiz me"*).
4. Dispatcher invokes the appropriate educational module.
5. Educational module prompts Gemini (with automatic model fallback).
6. Response is validated, saved to SQLite, and returned to client.
7. Frontend renders Markdown, builds interactive quiz cards, and displays follow-up chips.

---

## 17. Testing
Verified through a structured test hierarchy:
- `test_document_requirements.py`: 7/7 passed.
- `test_baseline.py`: 13/13 passed.
- `test_orchestrator.py`: 20/20 passed.
- `test_session.py`: 13/13 passed.
- `test_frontend.py`: 4/4 passed.
- Visual Quality Assurance: 4/4 viewports verified via browser snapshots.

---

## 18. Results
- 100% of the five original project document requirements are verified and operational.
- Response speed optimized with 0ms local intent classification for standard commands.
- Verified persistence across server restarts via SQLite.
- Seamless, modern AI workspace visual identity achieved.

---

## 19. Limitations
1. **Text-Centric Ingestion:** The current implementation processes textual input; direct ingestion of binary PDFs or images requires future multimodal extensions.
2. **Synchronous Quiz Flow:** Quizzes are generated as complete 3-question sets rather than single-question step-by-step branching trees.
3. **Local Model Hardware Footprint:** The optional local `LaMini-Flan-T5-783M` model requires ~3GB RAM; when unavailable, EduGenie gracefully falls back to Gemini.

---

## 20. Future Scope
- **Multimodal Document Upload:** Parsing textbook PDFs, slides, and diagrams.
- **Real-Time Voice Tutoring:** Bidirectional speech interface for auditory study.
- **Long-Term Mastery Analytics:** Spaced repetition scheduling and mastery tracking across multiple study sessions.
- **Collaborative Virtual Study Spaces:** Multi-user shared study sessions.

---

## 21. Conclusion
EduGenie demonstrates the practical application of modern generative AI in educational technology. By uniting Google Gemini's reasoning capabilities with structured educational workflows, persistent session memory, and a focused ambient interface, EduGenie delivers an effective, reliable, and engaging personal learning companion that satisfies all original project requirements and sets a strong foundation for future educational innovations.

---

## 22. References
1. Google AI for Developers. *Gemini API Documentation & Python SDK (`google-genai`)*. https://ai.google.dev/
2. FastAPI Documentation. *Modern, Fast, Asynchronous Web Framework for Python*. https://fastapi.tiangolo.com/
3. Pydantic Documentation. *Data Validation and Settings Management Using Python Type Annotations*. https://docs.pydantic.dev/
4. SQLite Consortium. *SQLite In-Process Database Engine*. https://www.sqlite.org/
5. EduGenie Original Project Document & Specification.
