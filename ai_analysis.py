"""
ai_analysis.py
---------------
AI se market ka plain-language analysis. Teen providers support hain (sab OPTIONAL):
  - Claude   (Anthropic)  -> key: https://console.anthropic.com
  - Gemini   (Google)     -> key: https://aistudio.google.com/apikey
  - ChatGPT  (OpenAI)     -> key: https://platform.openai.com/api-keys

User sidebar mein ek provider chunta hai aur uski key daalta hai. Bina AI ke
bhi tool poora chalta hai (rule-based signals). Har library optional import hoti
hai — jo install na ho, us provider ka friendly error aata hai (app crash nahi).
"""

import os

# -- optional imports (jo mile wahi provider available) --
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

# Har provider ka default (sasta + tez) model
DEFAULT_MODELS = {
    "claude": "claude-opus-4-8",
    "gemini": "gemini-2.0-flash",
    "chatgpt": "gpt-4o-mini",
}

# Provider ka aasan naam + key kahan se milti hai
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
    "Tum ek educational trading-analysis assistant ho. Tum market data aur "
    "technical indicators ka aasan zubaan mein analysis karte ho taake user "
    "seekhe ke market kya keh raha hai. Tum LICENSED financial advisor NAHI ho. "
    "Kabhi bhi definite 'yeh khareedo, paisa pakka banega' type advice mat do. "
    "Hamesha samjhao ke risk hota hai. Jawab Roman Urdu mein, chhota aur clear do."
)


def _installed(provider: str) -> bool:
    return {"claude": _HAS_CLAUDE, "gemini": _HAS_GEMINI, "chatgpt": _HAS_OPENAI}.get(provider, False)


def is_available(provider: str, api_key: str | None = None) -> bool:
    """Check ke chuna gaya provider use ho sakta hai (library + key)."""
    if not _installed(provider):
        return False
    return bool(api_key or os.environ.get(_ENV_KEYS.get(provider, "")))


def _build_prompt(market: str, symbol: str, signal: dict) -> str:
    reasons_text = "\n".join(f"- {r}" for r in signal.get("reasons", []))
    return (
        f"Market: {market.upper()} | Symbol: {symbol.upper()}\n"
        f"Current price: {signal.get('price')}\n"
        f"Rule-based signal: {signal.get('action')} (strength {signal.get('score')}%)\n"
        f"Indicators keh rahe hain:\n{reasons_text}\n\n"
        "Is data ki bunyaad par 3-4 line ka aasan analysis do: market abhi kya keh "
        "raha hai, aur user ko kis cheez par nazar rakhni chahiye. Risk ka zikr zaroor karo."
    )


def analyze(provider: str, market: str, symbol: str, signal: dict,
            api_key: str | None = None, model: str | None = None) -> str:
    """
    Chuna gaya provider se plain-language analysis. Error par friendly message
    (app kabhi crash nahi hota).
    """
    provider = provider.lower()
    if provider not in PROVIDERS:
        return f"Unknown AI provider: {provider}"
    if not _installed(provider):
        return f"{PROVIDERS[provider]['label']} ki library install nahi. Terminal mein install karein."

    key = api_key or os.environ.get(_ENV_KEYS[provider])
    if not key:
        return f"AI off — {PROVIDERS[provider]['label']} ki API key nahi mili. Sidebar mein daalein."

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
        return (f"{PROVIDERS[provider]['label']} se analysis nahi mil saka "
                f"(error: {e}). Rule-based signal upar phir bhi maujood hai.")
