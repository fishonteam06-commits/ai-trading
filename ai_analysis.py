"""
ai_analysis.py
---------------
Plain-language market analysis from AI. Three providers are supported (all OPTIONAL):
  - Claude   (Anthropic)  -> key: https://console.anthropic.com
  - Gemini   (Google)     -> key: https://aistudio.google.com/apikey
  - ChatGPT  (OpenAI)     -> key: https://platform.openai.com/api-keys

The user selects a provider in the sidebar and enters its key. The tool works fully
without AI too (rule-based signals). Each library is imported optionally — if one
isn't installed, that provider returns a friendly error (the app never crashes).
"""

import os

# -- optional imports (a provider is available only if its library is present) --
try:
    from anthropic import Anthropic
    _HAS_CLAUDE = True
except Exception:
    _HAS_CLAUDE = False

try:
    from google import genai as google_genai
    _HAS_GEMINI = True
except Exception:
    _HAS_GEMINI = False

try:
    from openai import OpenAI
    _HAS_OPENAI = True
except Exception:
    _HAS_OPENAI = False

# Each provider's default (cheap + fast) model
DEFAULT_MODELS = {
    "claude": "claude-opus-4-8",
    "gemini": "gemini-2.0-flash",
    "chatgpt": "gpt-4o-mini",
}

# Each provider's friendly name + where to get the key
PROVIDERS = {
    "claude":  {"label": "Claude (Anthropic)", "key_url": "https://console.anthropic.com"},
    "gemini":  {"label": "Gemini (Google)",    "key_url": "https://aistudio.google.com/apikey"},
    "chatgpt": {"label": "ChatGPT (OpenAI)",    "key_url": "https://platform.openai.com/api-keys"},
}

_ENV_KEYS = {
    "claude": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "chatgpt": "OPENAI_API_KEY",
}

_SYSTEM = (
    "You are an educational trading-analysis assistant. You analyse market data and "
    "technical indicators in plain language so the user can learn what the market is "
    "saying. You are NOT a licensed financial advisor. "
    "Never give definitive 'buy this, profit is guaranteed' type advice. "
    "Always explain that risk is involved. Answer in clear, professional English — keep it short and clear."
)


def _installed(provider: str) -> bool:
    return {"claude": _HAS_CLAUDE, "gemini": _HAS_GEMINI, "chatgpt": _HAS_OPENAI}.get(provider, False)


def is_available(provider: str, api_key: str | None = None) -> bool:
    """Check whether the chosen provider can be used (library + key)."""
    if not _installed(provider):
        return False
    return bool(api_key or os.environ.get(_ENV_KEYS.get(provider, "")))


def _build_prompt(market: str, symbol: str, signal: dict) -> str:
    reasons_text = "\n".join(f"- {r}" for r in signal.get("reasons", []))
    return (
        f"Market: {market.upper()} | Symbol: {symbol.upper()}\n"
        f"Current price: {signal.get('price')}\n"
        f"Rule-based signal: {signal.get('action')} (strength {signal.get('score')}%)\n"
        f"The indicators are saying:\n{reasons_text}\n\n"
        "Based on this data, give a simple 3-4 line analysis: what the market is saying "
        "right now, and what the user should keep an eye on. Be sure to mention the risk."
    )


def analyze(provider: str, market: str, symbol: str, signal: dict,
            api_key: str | None = None, model: str | None = None) -> str:
    """
    Plain-language analysis from the chosen provider. Returns a friendly message on
    error (the app never crashes).
    """
    provider = provider.lower()
    if provider not in PROVIDERS:
        return f"Unknown AI provider: {provider}"
    if not _installed(provider):
        return f"The {PROVIDERS[provider]['label']} library is not installed. Please install it in your terminal."

    key = api_key or os.environ.get(_ENV_KEYS[provider])
    if not key:
        return f"AI off — no API key found for {PROVIDERS[provider]['label']}. Please enter it in the sidebar."

    model = model or DEFAULT_MODELS[provider]
    prompt = _build_prompt(market, symbol, signal)

    try:
        if provider == "claude":
            client = Anthropic(api_key=key)
            resp = client.messages.create(
                model=model, max_tokens=500, system=_SYSTEM,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.content[0].text.strip()

        if provider == "gemini":
            client = google_genai.Client(api_key=key)
            resp = client.models.generate_content(
                model=model,
                contents=f"{_SYSTEM}\n\n{prompt}",
            )
            return (resp.text or "").strip()

        if provider == "chatgpt":
            client = OpenAI(api_key=key)
            resp = client.chat.completions.create(
                model=model, max_tokens=500,
                messages=[
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user", "content": prompt},
                ],
            )
            return resp.choices[0].message.content.strip()

    except Exception as e:
        return (f"Could not get analysis from {PROVIDERS[provider]['label']} "
                f"(error: {e}). The rule-based signal above is still available.")
