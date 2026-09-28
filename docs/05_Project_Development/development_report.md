# Phase 5: Project Development Phase — Implementation Report
## Project: EduGenie — Google Gemini Powered Learning Assistant

---

### 1. Technology Stack Summary

| Layer | Technologies Used | Justification |
| :--- | :--- | :--- |
| **Backend Framework** | Python 3.12, FastAPI 0.110+, Uvicorn 0.28+ | High-performance asynchronous execution, native OpenAPI docs, automatic Pydantic data validation. |
| **Generative AI** | Google Gemini (`google-genai` / `google-generativeai`) | State-of-the-art language comprehension, structured JSON output generation, rapid inference. |
| **Local Model (Optional)** | `MBZUAI/LaMini-Flan-T5-783M` (Hugging Face) | Offline sequence-to-sequence concept simplification with automated Gemini fallback. |
| **Persistence** | SQLite 3 (`edugenie.db`) | Embedded, serverless, zero-maintenance relational storage for multi-turn sessions and quiz state. |
| **Frontend UI** | Vanilla HTML5, CSS3, ES6 JavaScript | Zero npm/build-step overhead, instant page loads, universal browser compatibility. |
| **Visual Graphics** | HTML5 Canvas 2D API | Hardware-accelerated ambient particle/trail rendering with zero external library overhead. |
| **Data Serialization** | Pydantic v2 | Strict request/response typing, schema enforcement, and validation. |

---

### 2. Backend & Core Modules Implementation

#### 2.1 Academic Q&A (`qna.py`)
- **Function:** `answer_question_with_gemini(question: str) -> str`
- **Implementation:** Formulates a pedagogical prompt instructing Gemini to act as a supportive academic tutor. Enforces factual rigor, structured formatting, and concise clarity.

#### 2.2 Concept Explanation (`explanation_module.py`)
- **Function:** `explain_topic(topic: str) -> str`
- **Implementation:** Features a two-tiered execution model:
  1. Attempts to load local `LaMini-Flan-T5-783M` pipeline using PyTorch/Transformers if installed.
  2. If local weights are unavailable or memory is insufficient, seamlessly routes to Google Gemini with a prompt enforcing simple language, bulleted explanations, and everyday analogies.

#### 2.3 Quiz Generation (`quiz_module.py`)
- **Function:** `generate_quiz(topic_or_text: str) -> List[Dict[str, Any]]`
- **Implementation:** Employs few-shot prompt engineering instructing Gemini to produce exactly 3 multiple-choice questions in strict JSON format. Implements `clean_json_block()` and `validate_quiz_structure()` to strip Markdown code fences and guarantee each question has exactly 4 options and a valid answer key.

#### 2.4 Text Summarization (`summary_module.py`)
- **Function:** `summarize_text(text: str) -> str`
- **Implementation:** Processes input study passages, producing a dual-section output:
  - **Key Takeaways:** 3 to 5 clear bullet points.
  - **3-Sentence Summary:** High-density conceptual distillation.

#### 2.5 Learning Path Recommendations (`learning_path.py`)
- **Function:** `get_learning_recommendations(topic: str) -> Dict[str, Any]`
- **Implementation:** Queries Gemini to return a structured roadmap divided into:
  - **Beginner:** Core fundamentals and prerequisite knowledge.
  - **Intermediate:** Practical implementation, patterns, and problem solving.
  - **Advanced:** Architecture, performance optimization, and mastery topics.

---

### 3. Orchestration & Session Intelligence

#### 3.1 Intent Classification & Fast Pre-Router
- **Subsystem:** `orchestrator/intent_classifier.py`
- **Hybrid Intent Resolution:**
  - **Fast Local Pre-Router:** Evaluates regex patterns against user input (e.g., `^quiz (on|about)`, `^explain `, `^summarize `). Resolves common commands in $< 1\text{ ms}$ with $0\text{ token}$ API consumption.
  - **Gemini Intent Classifier:** For conversational or ambiguous prompts, invokes Gemini with few-shot classification examples to determine intent (`QA`, `EXPLAIN`, `QUIZ`, `SUMMARIZE`, `LEARNING_PATH`, `MULTI_ACTION`, `CLARIFICATION`, `UNKNOWN`).

#### 3.2 Context Engine & Anaphoric Resolution
- **Subsystem:** `orchestrator/context_engine.py`
- **Capability:** Analyzes rolling session history (up to 10 turns) to resolve contextual pronouns:
  - *"Explain that simpler"* $\rightarrow$ Extracts previous topic and invokes `explain_topic`.
  - *"Quiz me on it"* $\rightarrow$ Invokes `generate_quiz` for the active subject.
  - *"Can you give me a real-world example?"* $\rightarrow$ Expands on preceding explanation.

#### 3.3 Active Quiz Tracking & Evaluation
- **Subsystem:** `orchestrator/session_manager.py`
- When a quiz is delivered, questions and answer keys are saved to `quiz_sessions`.
- When the student replies with answers (e.g., *"1. A, 2. B, 3. C"* or *"I got the first one right and missed the others"*), the evaluator scores the submission, records weak concepts in `weak_areas_json`, and recommends targeted review.

---

### 4. Frontend & Interactive Visual Experience

#### 4.1 Layout Architecture (`templates/index.html` & `static/app.js`)
- Single-page conversational workspace supporting fluid transitions between `.state-home` and `.state-chat`.
- Interactive quiz rendering: Multiple-choice questions display clickable options that provide immediate green/red visual validation when selected.
- Asynchronous form handling with automatic textarea height auto-expansion, keyboard shortcut support (`Enter` to submit, `Shift+Enter` for newline), and latency measurement.

#### 4.2 Interactive Lightfall Background (`static/lightfall.js`)
- Custom-built HTML5 Canvas 2D ambient visual system.
- **Visual Design:** Continuous diagonal flowing light trails (~26° angle) falling with gentle organic sway across a deep `#050510` cosmic backdrop.
- **3-Tier Depth:** Slow, deep cosmic trails in violet; midground electric blue streaks; foreground cyan/white hero trails with optical tip flares.
- **Dynamic Adaptability:** Smoothly dims to $45\%$ opacity when entering chat mode to maintain optimal text contrast. Halts animation when `prefers-reduced-motion` is active.
