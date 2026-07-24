"""
auth.py  —  Security layer (login gate) with COOKIE persistence
================================================================
A password gate that remembers the login in a cookie — so it doesn't ask for
a login again on every reload or when the app is reopened on mobile.

Approach (robust, no extra library):
  - Reading the cookie : Streamlit's built-in `st.context.cookies` (instant, no rerun)
  - Writing the cookie : a small piece of JavaScript (document.cookie) at login time

Where the password is set (NEVER in the code):
  - Local testing : .streamlit/secrets.toml  ->  app_password = "yourpassword"
  - Streamlit Cloud : add the same line under the app's Settings -> Secrets
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
    """The token stored in the cookie — a non-reversible hash of the password."""
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
    """Read the cookie from the browser (Streamlit built-in — instant, no rerun)."""
    try:
        return st.context.cookies.get(COOKIE_NAME)
    except Exception:
        return None


def _write_cookie(token: str) -> None:
    """Set the cookie (on the parent page) — for 30 days."""
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
    """Call this at the start of the app. The login is remembered in a cookie."""
    # No password set at all (local dev) -> gate off, with a light warning.
    if not _configured():
        st.session_state["authed"] = True
        st.session_state["_no_pw_warning"] = True
        return

    # Already authed in this session? Then go straight through.
    if st.session_state.get("authed"):
        return

    # Cookie check — if a valid token is found, come in without logging in.
    token = _read_cookie()
    if token and hmac.compare_digest(str(token), _expected_token()):
        st.session_state["authed"] = True
        return

    # ---- Login form ----
    st.markdown("## 🔒 AI Trading Assistant — Login")
    st.caption("This app is private. Log in once — it will then be remembered.")
    with st.form("login_form"):
        pw = st.text_input("Password", type="password")
        remember = st.checkbox("Remember me on this device (don't ask to log in)", value=True)
        ok = st.form_submit_button("🔓 Login", type="primary")

    if ok:
        if _password_ok(pw):
            st.session_state["authed"] = True
            st.session_state["login_attempts"] = 0
            if remember:
                _write_cookie(_expected_token())
                # give the cookie a moment to be set in the browser
                st.success("Login successful! Loading...")
                time.sleep(0.6)
            st.rerun()
        else:
            attempts = st.session_state.get("login_attempts", 0) + 1
            st.session_state["login_attempts"] = attempts
            if attempts >= 3:
                st.error("Too many incorrect passwords. Please wait a moment.")
                time.sleep(min(attempts, 8))
            else:
                st.error("Incorrect password. Please try again.")

    st.stop()


def logout_button() -> None:
    """Logout button in the sidebar (shown when logged in)."""
    if st.session_state.get("authed") and _configured():
        if st.sidebar.button("🔒 Logout"):
            _clear_cookie()
            st.session_state["authed"] = False
            time.sleep(0.4)
            st.rerun()


def hash_password(plain: str) -> str:
    """Helper: SHA-256 hash of the password (for putting into secrets)."""
    return hashlib.sha256(plain.encode()).hexdigest()
