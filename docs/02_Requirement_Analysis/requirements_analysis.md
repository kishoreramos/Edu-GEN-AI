# Phase 2: Requirement Analysis Phase
## Project: EduGenie — Google Gemini Powered Learning Assistant

---

### 1. Project Title
**EduGenie — Google Gemini Powered Learning Assistant**

---

### 2. Problem Statement
Traditional digital educational resources present learners with passive, unguided experiences:
1. Search engines provide millions of links without synthesizing targeted answers.
2. Textbooks present dense jargon without adapting explanations to beginner levels.
3. Formative self-testing requires searching for separate quiz banks that rarely align with the specific material just studied.
4. Learners lack personalized study sequences that organize prerequisites logically.

EduGenie addresses these deficits by unifying Question Answering, Simplified Concept Explanation, Automated Quiz Generation, Text Summarization, and Structured Learning Paths into a single responsive platform.

---

### 3. Project Objectives
- **Primary Objective:** Build a robust, responsive AI learning companion leveraging Google Gemini to facilitate active, student-centered learning.
- **Pedagogical Objectives:**
  - Provide accurate, factually grounded answers to direct student inquiries.
  - Simplify complex academic concepts into intuitive analogies without sacrificing correctness.
  - Reinforce memory retention through on-demand 3-question multiple-choice quizzes.
  - Distill extensive study materials into key bullet points and high-level summaries.
  - Generate structured, 3-tiered learning roadmaps (Beginner, Intermediate, Advanced).
- **Architectural Objectives:**
  - Build an asynchronous, modular backend using FastAPI.
  - Support dual Gemini SDK integrations (`google-genai` and `google-generativeai`) with automated model fallback.
  - Maintain 100% backwards compatibility with all five original documented endpoints.
  - Provide a lightweight, zero-framework vanilla frontend with GPU-accelerated ambient visuals.

---

### 4. Functional Requirements (FR)

#### Original Core Requirements (Baseline)
- **FR-01: Academic Question & Answer**
  - The system must accept an academic question and return a concise, accurate answer using Google Gemini.
  - Input validation must reject empty or whitespace-only queries.
- **FR-02: Simplified Concept Explanation**
  - The system must accept a topic and generate a clear, beginner-friendly explanation incorporating everyday analogies.
  - Support an optional local sequence-to-sequence model (`LaMini-Flan-T5-783M`) with automatic fallback to Gemini if local model weights are absent.
- **FR-03: Multiple-Choice Quiz Generation**
  - The system must accept a topic or text and generate a structured 3-question multiple-choice quiz.
  - Each question must contain exactly 4 options, a clearly designated correct answer, and valid JSON structure.
- **FR-04: Educational Text Summarization**
  - The system must take input text and produce an organized summary consisting of key takeaways and a 3-sentence summary.
- **FR-05: Learning Path Recommendations**
  - The system must accept a subject or skill and return a sequential roadmap categorized into Beginner, Intermediate, and Advanced milestones.
- **FR-06: Documented Direct Endpoints**
  - The backend must expose dedicated HTTP endpoints for direct programmatic consumption:
    - `POST /qa` (and `GET /qa?question=...`)
    - `POST /explain`
    - `POST /quiz`
    - `POST /summarize`
    - `POST /learn/recommendations` (and `GET /learn/recommendations?topic=...`)

#### Subsequent Architectural Enhancements
- **FR-07: Conversational AI Orchestrator (`POST /api/chat`)**
  - The system must provide a unified endpoint that accepts conversational text, classifies intent, and routes to the appropriate educational module.
- **FR-08: Persistent Multi-Turn Session Memory**
  - The system must persist conversation history across server restarts using a local SQLite database (`edugenie.db`).
  - Context engine must resolve anaphoric follow-up requests (*"explain that"*, *"quiz me on it"*, *"give an example"*).
- **FR-09: Active Quiz State Tracking & Score Evaluation**
  - When a quiz is generated in chat mode, the session must track the active quiz, accept user answers, calculate scores, and provide remedial feedback.
- **FR-10: Single-Box Unified Frontend**
  - The web interface must allow users to interact via a single prompt box with optional task-chip overrides (Auto, Explain, Q&A, Quiz, Summary, Learning Path).

---

### 5. Non-Functional Requirements (NFR)
- **NFR-01: Response Latency**
  - Intent classification must execute within < 5ms for keyword-matched patterns.
  - API responses must leverage bounded timeouts (under 10s) to prevent hanging requests.
- **NFR-02: Reliability & Model Fallback**
  - The system must automatically cascade between available Gemini models (e.g., `gemini-2.5-flash`, `gemma-4-26b-a4b-it`) to maintain 100% uptime even if a specific model endpoint is deprecated or rate-limited.
- **NFR-03: Security & Credential Isolation**
  - API keys must be loaded strictly from local `.env` files via `python-dotenv`.
  - Keys and databases must be explicitly excluded from Git version control via `.gitignore`.
- **NFR-04: Lightweight & Portable Footprint**
  - Zero heavy frontend dependencies (no Node.js build step, no React/Webpack overhead).
  - Backend must run directly on standard Python 3.10+ environments.
- **NFR-05: Accessibility & Responsiveness**
  - Responsive design supporting viewports from mobile (390px) to desktop (1920px).
  - Respect `prefers-reduced-motion` accessibility standards by halting canvas animations when requested.

---

### 6. User Requirements (UR)
- **UR-01:** Students must be able to ask any study-related question without having to configure complex parameters.
- **UR-02:** Students must receive interactive feedback (e.g., clickable quiz option buttons, instant correctness validation).
- **UR-03:** Students must be able to switch topics or start a new conversation session with a single click.

---

### 7. System Requirements
- **Runtime Environment:** Python 3.10, 3.11, or 3.12 (Tested on Python 3.12).
- **Operating System:** Platform independent (Windows 10/11, macOS, Linux).
- **Memory Requirements:**
  - Base Gemini mode: 512MB RAM minimum.
  - Local LaMini mode (optional): 4GB RAM + PyTorch.
- **Network Requirements:** Outbound HTTPS connectivity to `generativelanguage.googleapis.com`.
- **Client Requirements:** Modern web browser supporting HTML5 Canvas (Chrome, Edge, Firefox, Safari).

---

### 8. Feature Traceability Matrix: Original Baseline vs. Enhancements

| Feature ID | Feature Name | Original Document Requirement | Phase Added / Enhanced | Status |
| :--- | :--- | :---: | :---: | :---: |
| **REQ-01** | Academic Q&A (`/qa`) | **Yes** | Phase 1 (Baseline) | Verified / Complete |
| **REQ-02** | Concept Explanation (`/explain`) | **Yes** | Phase 1 (Baseline) | Verified / Complete |
| **REQ-03** | Quiz Generation (`/quiz`) | **Yes** | Phase 1 (Baseline) | Verified / Complete |
| **REQ-04** | Text Summarization (`/summarize`) | **Yes** | Phase 1 (Baseline) | Verified / Complete |
| **REQ-05** | Learning Path (`/learn/recommendations`) | **Yes** | Phase 1 (Baseline) | Verified / Complete |
| **REQ-06** | Five Dedicated REST Endpoints | **Yes** | Phase 1 (Baseline) | Verified / Complete |
| **REQ-07** | Intelligent Intent Router (`POST /api/chat`) | Enhancement | Phase 2 | Verified / Complete |
| **REQ-08** | Multi-Turn SQLite Session Persistence | Enhancement | Phase 3 | Verified / Complete |
| **REQ-09** | Interactive Quiz Widget & State Tracking | Enhancement | Phase 3 | Verified / Complete |
| **REQ-10** | Unified Single-Composer Chat Interface | Enhancement | Phase 4 & 6 | Verified / Complete |
| **REQ-11** | Zero-Latency Fast Local Intent Classifier | Enhancement | Phase 6 | Verified / Complete |
| **REQ-12** | Interactive Ambient Lightfall Visuals | Enhancement | Phase 6.5 | Verified / Complete |
