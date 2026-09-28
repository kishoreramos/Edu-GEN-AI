# Explanation Module - EduGenie
import logging

try:
    from .config import generate_gemini_text, is_gemini_configured, GEMINI_KEY_MISSING_ERROR, GEMINI_MODEL
except ImportError:
    from config import generate_gemini_text, is_gemini_configured, GEMINI_KEY_MISSING_ERROR, GEMINI_MODEL

logger = logging.getLogger("EduGenie.Explanation")

# Lazy holders for local Hugging Face model
_local_model_attempted = False
_local_model = None
_local_tokenizer = None

def _load_local_lamini_model():
    """
    Attempts to load the documented local LaMini-Flan-T5-783M model.
    Catches import errors or resource/memory constraints without crashing.
    """
    global _local_model_attempted, _local_model, _local_tokenizer
    if _local_model_attempted:
        return _local_model, _local_tokenizer

    _local_model_attempted = True
    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        import torch

        model_name = "MBZUAI/LaMini-Flan-T5-783M"
        logger.info(f"Attempting to load local explanation model '{model_name}'...")
        _local_tokenizer = AutoTokenizer.from_pretrained(model_name)
        _local_model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        logger.info("Local LaMini-Flan-T5 model loaded successfully.")
        return _local_model, _local_tokenizer
    except Exception as e:
        logger.warning(
            f"Local model 'MBZUAI/LaMini-Flan-T5-783M' could not be loaded ({e}). "
            "Falling back to Gemini for simplified concept explanation."
        )
        _local_model = None
        _local_tokenizer = None
        return None, None

def explain_topic(topic: str) -> str:
    """
    Explains an educational concept in simple, beginner-friendly terms.
    Tries the documented local LaMini-Flan-T5 model first;
    falls back cleanly to Gemini with the same school-student prompt.
    """
    if not topic or not topic.strip():
        return "⚠️ Error: Please provide a valid topic to explain."

    clean_topic = topic.strip()
    prompt_text = f"Explain the concept of '{clean_topic}' in a simple and clear way for a school student."

    # 1. Attempt documented local model
    local_model, local_tokenizer = _load_local_lamini_model()
    if local_model is not None and local_tokenizer is not None:
        try:
            inputs = local_tokenizer(prompt_text, return_tensors="pt")
            outputs = local_model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.7,
                top_k=50,
                top_p=0.95,
                do_sample=True
            )
            return local_tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception as e:
            logger.error(f"Error during local model inference: {e}. Falling back to Gemini.")

    # 2. Fallback to Gemini with educational prompt
    if not is_gemini_configured():
        return (
            f"⚠️ Explanation Engine Notice: Local model (LaMini-Flan-T5) is not loaded, "
            f"and {GEMINI_KEY_MISSING_ERROR}"
        )

    try:
        return generate_gemini_text(prompt_text)
    except Exception as e:
        logger.error(f"Error in Gemini explanation fallback: {e}", exc_info=True)
        return f"⚠️ Error in Explanation: {str(e)}"

