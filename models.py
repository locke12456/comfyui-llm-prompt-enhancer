"""Model choices for each LLM provider.

Lists are ordered most capable first, cheapest last. Defaults point at the cheap
tier on purpose: prompt enhancement is a short, easy task and the small models
handle it well for a fraction of the cost.

Model IDs verified against provider docs on 2026-08-16. Providers rename and
retire models regularly, so re-check these when something starts returning 404.
"""

import logging
import os

try:
    import anthropic
except ImportError:
    anthropic = None

logger = logging.getLogger(__name__)

# https://developers.openai.com/api/docs/models
OPENAI_MODELS = [
    "gpt-5.6-sol",     # flagship, $5 / $30 per Mtok
    "gpt-5.6-terra",   # balanced, $2 / $12
    "gpt-5.6-luna",    # cost optimized, $0.20 / $1.20
]
OPENAI_DEFAULT = "gpt-5.6-luna"

# https://platform.claude.com/docs/en/about-claude/models/overview
ANTHROPIC_MODELS = [
    "claude-opus-5-5",    # flagship, $4 / $20 per Mtok
    "claude-sonnet-5-5",  # balanced, $2 / $10
    "claude-haiku-5-5",   # fastest and cheapest, $0.10 / $0.50
]
ANTHROPIC_DEFAULT = "claude-haiku-5-5"


def fetch_anthropic_models(api_key):
    """Ask the Models API for the current Claude list. Raises anthropic.APIError on failure."""
    fetched = [m.id for m in anthropic.Anthropic(api_key=api_key).models.list(limit=100)]
    if not fetched:
        return list(ANTHROPIC_MODELS)
    if ANTHROPIC_DEFAULT not in fetched:
        fetched.append(ANTHROPIC_DEFAULT)
    return fetched


def _initial_anthropic_models():
    """Use ANTHROPIC_API_KEY at load time; fall back to the hardcoded list so the node still loads offline."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic is None or not api_key:
        return ANTHROPIC_MODELS
    try:
        return fetch_anthropic_models(api_key)
    except anthropic.APIError as e:
        logger.warning(f"Could not fetch Claude models, using built-in list: {e}")
        return ANTHROPIC_MODELS


ANTHROPIC_MODELS = _initial_anthropic_models()

# https://ai.google.dev/gemini-api/docs/models
GOOGLE_MODELS = [
    "gemini-3.1-pro-preview",  # flagship, 2M context
    "gemini-3.7-flash",        # newest workhorse, intro pricing through 2026-12-31
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",   # low latency, high volume
    "gemini-3.1-flash-lite",   # cheapest, $0.25 / $1.50
]
GOOGLE_DEFAULT = "gemini-3.5-flash-lite"

# OpenRouter exposes thousands of models, so this stays a free text field.
# The old default (google/gemma-2-9b-it:free) was retired and now 404s.
OPENROUTER_DEFAULT = "google/gemma-4-26b-a4b-it:free"

# Ollama runs locally, so the model list depends on whatever the user pulled.
OLLAMA_DEFAULT = "llama3.2:1b"
OLLAMA_HOST_DEFAULT = "http://localhost:11434"
