# Phase 5: Project Development Phase — Codebase & Development Evidence
## Project: EduGenie — Google Gemini Powered Learning Assistant

---

### 1. Codebase Inventory & Purpose

Below is an inventory of all actual source code, asset, and configuration files comprising the EduGenie repository:

```
c:\kishoreProject\EduGenie\
│
├── main.py                          # FastAPI application, route declarations, and lifecycle management
├── config.py                        # Centralized Gemini SDK configuration, API keys, and model fallback
├── qna.py                           # Academic Q&A module powered by Google Gemini
├── explanation_module.py            # Concept explanation module (LaMini local model with Gemini fallback)
├── quiz_module.py                   # Multiple-choice quiz generator with strict JSON validation
├── summary_module.py                # Educational text summarization module
├── learning_path.py                 # 3-tier learning roadmap generator
│
├── orchestrator/                    # Conversational orchestration package
│   ├── __init__.py                  # Package initializer
│   ├── schemas.py                   # Pydantic data models (ChatRequest, ChatResponse, IntentType)
│   ├── router.py                    # Message processor and capability dispatcher
│   ├── intent_classifier.py         # Zero-latency regex pre-router + Gemini few-shot classifier
│   ├── context_engine.py            # Contextual pronoun and anaphoric reference resolution
│   ├── session_manager.py           # SQLite session persistence and active quiz evaluation
│   └── workflow.py                  # Sequential multi-action execution pipeline
│
├── static/                          # Frontend client assets
│   ├── app.js                       # Client controller: chat state, markdown rendering, quiz interaction
│   ├── style.css                    # Unified design system: dark celestial theme, responsive layout
│   └── lightfall.js                 # Standalone Canvas 2D ambient Lightfall background effect
│
├── templates/                       # Jinja2 template views
│   └── index.html                   # Single-page HTML5 workspace markup
│
├── requirements.txt                 # Python project dependencies
├── .env.example                     # Sanitized environment template for API keys
├── .gitignore                       # Git rules excluding .env, SQLite databases, and virtualenvs
├── edugenie.db                      # Local SQLite database storing sessions and message history
│
└── tests & verification/            # Actual verification suites
    ├── test_document_requirements.py# Bounded verification suite for original 5 requirements (7/7 passed)
    ├── test_baseline.py             # Unit tests for baseline endpoints (13/13 passed)
    ├── test_orchestrator.py         # Unit tests for intent classifier and router (20/20 passed)
    ├── test_session.py              # Unit tests for SQLite session persistence (13/13 scenarios passed)
    ├── test_frontend.py             # Frontend asset availability and endpoint tests (4/4 passed)
    └── smoke_test.py                # Fast connectivity check for Gemini API
```

---

### 2. Functional Mapping of Key Files

| File Path | Functional Role | Primary Dependencies |
| :--- | :--- | :--- |
| `main.py` | Exposes REST endpoints (`/qa`, `/explain`, `/quiz`, `/summarize`, `/learn/recommendations`, `/api/chat`, `/api/session`, `/api/sessions`). | `fastapi`, `jinja2`, `uvicorn`, `pydantic` |
| `config.py` | Configures client credentials, detects SDK version, manages fallback sequence between `gemini-2.5-flash` and `gemma-4-26b-a4b-it`. | `google-genai`, `google-generativeai`, `python-dotenv` |
| `qna.py` | Implements `answer_question_with_gemini()`. Validates non-empty input and queries Gemini. | `config.py` |
| `explanation_module.py` | Implements `explain_topic()`. Manages optional local transformer model and Gemini fallback. | `config.py` |
| `quiz_module.py` | Implements `generate_quiz()`, `validate_quiz_structure()`, and `clean_json_block()`. | `json`, `re`, `config.py` |
| `summary_module.py` | Implements `summarize_text()`. Generates structured key takeaways and 3-sentence summary. | `config.py` |
| `learning_path.py` | Implements `get_learning_recommendations()`. Generates 3-tier roadmap. | `config.py` |
| `orchestrator/router.py` | Orchestrates user messages, checks active quiz state, routes to educational modules, and returns `ChatResponse`. | `orchestrator.schemas`, `orchestrator.intent_classifier` |
| `orchestrator/session_manager.py` | Manages SQLite connection, executes schema creation, persists messages, and updates quiz scores. | `sqlite3`, `json`, `uuid` |
| `static/app.js` | Manages UI state (`.state-home` vs. `.state-chat`), renders Markdown, builds interactive quiz cards, and sends requests to `/api/chat`. | Vanilla DOM API |
| `static/lightfall.js` | Custom Canvas 2D ambient background. Renders curved diagonal trails with 3-tier depth, celestial bloom, and pointer deflection. | HTML5 Canvas 2D |
| `static/style.css` | Implements the dark celestial theme (`#050510`), CSS variables, glassmorphism, and responsive breakpoints. | CSS3 |
| `templates/index.html` | Semantic single-page HTML layout containing header, hero section, message stream, and docked composer. | HTML5 |

---

### 3. Verification of Zero Third-Party Frontend Dependencies
- **No Node.js or npm dependencies:** The frontend contains zero `node_modules` folders, zero Webpack/Vite build configs, and zero external JS runtime requirements.
- **Self-contained execution:** The entire application runs directly with `uvicorn main:app` using standard Python packages.
