# EduGenie Configuration & AI Model Setup
import os
import re
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("EduGenie.Config")

# Load environment variables from .env file
ENV_PATH = Path(__file__).resolve().parent / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()


# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
DEFAULT_MODEL_NAME = GEMINI_MODEL  # Backwards compatibility alias

# Candidate fallback models in priority order if configured model is retired/unavailable/rate-limited
FALLBACK_MODELS: List[str] = ["gemma-4-26b-a4b-it", "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3-flash-preview", "gemini-3.6-flash", "gemini-2.5-flash"]

# Cached verified active model after runtime check
_active_working_model: Optional[str] = None

# Warning message when API key is not configured
GEMINI_KEY_MISSING_ERROR = (
    "⚠️ Gemini API key is not configured. Please set GEMINI_API_KEY in your .env file."
)

_genai_client = None

def is_gemini_configured() -> bool:
    """Check if the Gemini API key is provided and non-empty."""
    return bool(GEMINI_API_KEY and GEMINI_API_KEY != "your_key_here")

def get_genai_client():
    """
    Returns an initialized client from the modern 'google.genai' SDK (v2.x).
    """
    global _genai_client
    if not is_gemini_configured():
        return None

    if _genai_client is None:
        try:
            from google import genai
            from google.genai import types
            _genai_client = genai.Client(
                api_key=GEMINI_API_KEY,
                http_options=types.HttpOptions(client_args={"timeout": 30.0})
            )
            logger.info("Initialized modern google.genai Client with 30s request timeout.")
        except Exception as e:
            logger.error(f"Failed to initialize google.genai Client: {e}")
            _genai_client = None
    return _genai_client

def _sanitize_error(error_msg: str) -> str:
    """Removes sensitive keys, tokens, or paths from error messages."""
    if not error_msg:
        return ""
    cleaned = re.sub(r'AIza[0-9A-Za-z_-]{35}', '[REDACTED_API_KEY]', str(error_msg))
    cleaned = re.sub(r'AQ\.[0-9A-Za-z_-]{20,}', '[REDACTED_API_KEY]', cleaned)
    return cleaned

def generate_gemini_text(prompt: str, model_name: str = None) -> str:
    """
    Generates text using the modern google.genai SDK with centralized model configuration,
    automatic model fallback if configured model is retired/unavailable, and legacy SDK fallback.
    """
    global _active_working_model

    if not is_gemini_configured():
        return GEMINI_KEY_MISSING_ERROR

    if not prompt or not str(prompt).strip():
        return "⚠️ Error: Prompt cannot be empty."

    # Determine candidate model sequence
    primary_model = _active_working_model or model_name or GEMINI_MODEL
    models_to_try = [primary_model]
    for fb in FALLBACK_MODELS:
        if fb not in models_to_try:
            models_to_try.append(fb)
    # Bound to at most 3 candidate models to prevent excessive waiting
    models_to_try = models_to_try[:3]

    # 1. Try modern google.genai SDK
    client = get_genai_client()
    last_error = None
    if client is not None:
        for mod in models_to_try:
            try:
                response = client.models.generate_content(
                    model=mod,
                    contents=prompt
                )
                if hasattr(response, "text") and response.text:
                    if _active_working_model != mod:
                        _active_working_model = mod
                        logger.info(f"Using active verified Gemini model: {mod}")
                    return response.text.strip()
            except Exception as e:
                last_error = e
                err_text = str(e)
                logger.warning(f"google.genai call failed with model '{mod}': {_sanitize_error(err_text)}")
                # If the error is an auth failure (401/403), break immediately; otherwise try alternate model
                if "401" in err_text or "403" in err_text or "PERMISSION_DENIED" in err_text:
                    break
                # If rate-limited, wait briefly before trying next fallback model (bounded to max 3s)
                if "429" in err_text or "RESOURCE_EXHAUSTED" in err_text:
                    import time
                    logger.info(f"Gemini RPM rate limit encountered on '{mod}'. Bounded backoff 3s...")
                    time.sleep(3)

    # Format user-friendly backend error
    sanitized_err = _sanitize_error(str(last_error)) if last_error else "Model unavailable"
    if "404" in sanitized_err or "NOT_FOUND" in sanitized_err:
        return f"⚠️ Error: The configured Gemini model '{primary_model}' is unavailable. Please verify GEMINI_MODEL in .env."
    elif "429" in sanitized_err or "RESOURCE_EXHAUSTED" in sanitized_err:
        return "⚠️ Error: Gemini API rate limit or quota exceeded. Please try again shortly."
    elif "403" in sanitized_err or "PERMISSION_DENIED" in sanitized_err:
        return "⚠️ Error: Gemini API permission denied. Please verify your GEMINI_API_KEY."

    return f"⚠️ Error: Unable to generate response from Gemini ({sanitized_err})."

class GeminiModelAdapter:
    """Adapter providing backward-compatible .generate_content() interface."""
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate_content(self, contents: str):
        text = generate_gemini_text(contents, model_name=self.model_name)
        class ResponseAdapter:
            def __init__(self, txt):
                self.text = txt
                self.parts = []
        return ResponseAdapter(text)

def get_gemini_model(model_name: str = None):
    """
    Returns a model instance or adapter for backward compatibility.
    Uses the centrally configured GEMINI_MODEL.
    """
    if not is_gemini_configured():
        logger.warning("GEMINI_API_KEY is missing or empty. Gemini calls will return configuration warning.")
        return None

    selected_model = model_name or GEMINI_MODEL
    return GeminiModelAdapter(selected_model)

def verify_gemini_models_safe() -> Dict[str, Any]:
    """
    Safe API-level verification tool that queries available models
    without printing or exposing the API key.
    """
    if not is_gemini_configured():
        return {"configured": False, "error": "API key not configured"}

    client = get_genai_client()
    if client is None:
        return {"configured": True, "client_ready": False, "error": "Could not create genai Client"}

    try:
        models = list(client.models.list())
        model_names = [m.name for m in models]
        active = _active_working_model or GEMINI_MODEL
        return {
            "configured": True,
            "client_ready": True,
            "configured_model": GEMINI_MODEL,
            "active_working_model": active,
            "total_available_models": len(model_names),
            "sample_models": model_names[:10]
        }
    except Exception as e:
        return {
            "configured": True,
            "client_ready": True,
            "error": _sanitize_error(str(e))
        }
