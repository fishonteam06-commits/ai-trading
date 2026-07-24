"""
auth.py  —  Security layer (login gate) with COOKIE persistence
================================================================
Password gate jo login ko ek cookie mein yaad rakhta hai — taake reload par
ya mobile par app dobara kholne par bar bar login na maange.

Tareeka (robust, koi extra library nahi):
  - Cookie PADHNA  : Streamlit ka built-in `st.context.cookies` (foran, no rerun)
  - Cookie LIKHNA  : chhoti JavaScript (document.cookie) — login ke waqt

Password kahan set hota hai (code mein KABHI nahi):
  - Local test : .streamlit/secrets.toml  ->  app_password = "yourpassword"
  - Streamlit Cloud : app ke Settings -> Secrets  mein wahi line daalein
"""

import hashlib
import hmac
import time

import streamlit as st
import streamlit.components.v1 as components

COOKIE_DAYS = 30
COOKIE_NAME = "ai_trading_auth"
_SALT = "ai-trading-assistant|v1"


def _get_secret(name: str, default=None):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


def _configured() -> bool:
    return bool(_get_secret("app_password") or _get_secret("app_password_hash"))


def _expected_token() -> str:
    """Cookie mein rakha jaane wala token — password ka non-reversible hash."""
    hashed = _get_secret("app_password_hash")
    if not hashed:
        plain = _get_secret("app_password")
        hashed = hashlib.sha256(str(plain).encode()).hexdigest() if plain else ""
    return hashlib.sha256((str(hashed) + _SALT).encode()).hexdigest()


def _password_ok(entered: str) -> bool:
    hashed = _get_secret("app_password_hash")
    if hashed:
        entered_hash = hashlib.sha256(entered.encode()).hexdigest()
        return hmac.compare_digest(entered_hash, str(hashed))
    plain = _get_secret("app_password")
    if plain:
        return hmac.compare_digest(entered, str(plain))
    return False


def _read_cookie() -> str | None:
    """Browser se cookie padho (Streamlit built-in — foran, no rerun)."""
    try:
        return st.context.cookies.get(COOKIE_NAME)
    except Exception:
        return None


def _write_cookie(token: str) -> None:
    """Cookie set karo (parent page par) — 30 din ke liye."""
    max_age = COOKIE_DAYS * 24 * 60 * 60
    components.html(
        f"""
        <script>
        try {{
          var c = "{COOKIE_NAME}={token}; path=/; max-age={max_age}; SameSite=Lax";
          window.parent.document.cookie = c;
        }} catch (e) {{
          document.cookie = "{COOKIE_NAME}={token}; path=/; max-age={max_age}; SameSite=Lax";
        }}
        </script>
        """,
        height=0,
    )


def _clear_cookie() -> None:
    components.html(
        f"""
        <script>
        try {{
          window.parent.document.cookie = "{COOKIE_NAME}=; path=/; max-age=0; SameSite=Lax";
        }} catch (e) {{
          document.cookie = "{COOKIE_NAME}=; path=/; max-age=0; SameSite=Lax";
        }}
        </script>
        """,
        height=0,
    )


def require_login() -> None:
    """App ke shuru mein call karein. Login cookie mein yaad rehta hai."""
    # Password set hi nahi (local dev) -> gate off, halki warning.
    if not _configured():
        st.session_state["authed"] = True
        st.session_state["_no_pw_warning"] = True
        return

    # Is session mein pehle se authed? To seedha aage.
    if st.session_state.get("authed"):
        return

    # Cookie check — valid token mila to bina login ke andar.
    token = _read_cookie()
    if token and hmac.compare_digest(str(token), _expected_token()):
        st.session_state["authed"] = True
        return

    # ---- Login form ----
    st.markdown("## 🔒 AI Trading Assistant — Login")
    st.caption("Yeh app private hai. Ek dafa login karein — phir yaad rahega.")
    with st.form("login_form"):
        pw = st.text_input("Password", type="password")
        remember = st.checkbox("Is device par yaad rakhein (login na maange)", value=True)
        ok = st.form_submit_button("🔓 Login", type="primary")

    if ok:
        if _password_ok(pw):
            st.session_state["authed"] = True
            st.session_state["login_attempts"] = 0
            if remember:
                _write_cookie(_expected_token())
                # cookie browser mein set hone ke liye ek lamha
                st.success("Login kamyab! Load ho raha hai...")
                time.sleep(0.6)
            st.rerun()
        else:
            attempts = st.session_state.get("login_attempts", 0) + 1
            st.session_state["login_attempts"] = attempts
            if attempts >= 3:
                st.error("Bar bar ghalat password. Thora intezaar karein.")
                time.sleep(min(attempts, 8))
            else:
                st.error("Ghalat password. Dobara koshish karein.")

    st.stop()


def logout_button() -> None:
    """Sidebar mein logout button (login on hone par)."""
    if st.session_state.get("authed") and _configured():
        if st.sidebar.button("🔒 Logout"):
            _clear_cookie()
            st.session_state["authed"] = False
            time.sleep(0.4)
            st.rerun()


def hash_password(plain: str) -> str:
    """Helper: password ka SHA-256 hash (secrets mein daalne ke liye)."""
    return hashlib.sha256(plain.encode()).hexdigest()
