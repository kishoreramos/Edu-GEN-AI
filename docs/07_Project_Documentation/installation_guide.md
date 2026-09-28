# Phase 7: Project Documentation — Installation & Setup Guide
## Project: EduGenie — Google Gemini Powered Learning Assistant

---

### 1. Prerequisites
Before installing EduGenie, ensure your environment meets the following requirements:
- **Operating System:** Windows 10/11, macOS, or Linux.
- **Python:** Python 3.10, 3.11, or 3.12 (Tested on Python 3.12).
- **Git:** Git 2.30+ installed.
- **Google AI Studio Account:** A free Google Gemini API key from [Google AI Studio](https://aistudio.google.com/).
- **Web Browser:** Modern browser supporting HTML5 Canvas (Google Chrome, Microsoft Edge, Mozilla Firefox, or Safari).

---

### 2. Step-by-Step Installation

#### Step 1: Clone or Navigate to the Repository
```bash
# Clone the repository (if cloning from GitHub)
git clone <repository_url>
cd EduGenie

# Or navigate directly if already in workspace
cd c:\kishoreProject\EduGenie
```

#### Step 2: Create and Activate a Virtual Environment
```bash
# Windows (PowerShell / Command Prompt)
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

#### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

Verify that key packages are installed properly:
- `fastapi`
- `uvicorn`
- `google-genai`
- `pydantic`
- `jinja2`
- `python-dotenv`

---

### 3. Environment Configuration

1. Locate `.env.example` in the `EduGenie` root folder.
2. Copy it to create your local `.env` file:
   ```bash
   # Windows (PowerShell)
   Copy-Item .env.example .env

   # Linux / macOS
   cp .env.example .env
   ```
3. Open `.env` in any text editor and supply your Gemini API key:
   ```env
   # Google Gemini API Key
   GEMINI_API_KEY=AIzaSyYourActualGeminiApiKeyHere

   # Centralized Gemini Model Selection
   GEMINI_MODEL=gemini-2.5-flash

   # Server Configuration (optional)
   PORT=8000
   HOST=127.0.0.1
   ```

> **IMPORTANT SECURITY NOTE:** Never commit your `.env` file to Git. It is automatically ignored by `.gitignore`.

---

### 4. Running the Application

Launch the FastAPI application using Uvicorn:

```bash
# Directly from the EduGenie folder:
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Once running, Uvicorn will log:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

### 5. Accessing the Application

- **Web User Interface:** Open your browser and navigate to:
  ```
  http://127.0.0.1:8000
  ```
- **Interactive Swagger API Documentation:**
  ```
  http://127.0.0.1:8000/docs
  ```
- **Alternative ReDoc Documentation:**
  ```
  http://127.0.0.1:8000/redoc
  ```

---

### 6. Troubleshooting Common Setup Issues

| Issue | Cause | Resolution |
| :--- | :--- | :--- |
| `Address already in use` (Port 8000) | Another process is occupying port 8000. | Terminate the occupying process or run on a different port: `--port 8001`. |
| `Gemini API key not configured` | `.env` file missing or empty `GEMINI_API_KEY`. | Create `.env` from `.env.example` and insert a valid API key. |
| `ModuleNotFoundError` | Dependencies not installed in active environment. | Ensure `.venv` is activated (`.venv\Scripts\activate`) and run `pip install -r requirements.txt`. |
| `Model not found / 404` | Deprecated model name in configuration. | EduGenie automatically falls back to an active working model (`gemma-4-26b-a4b-it`). Ensure network connectivity to Google. |
