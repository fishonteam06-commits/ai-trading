"""
auth.py  —  Security layer (login gate)
========================================
Public/online app ke liye ek password gate. Sirf jise password pata ho wahi
app khol sakta hai — taake ajnabi log aapki app aur AI keys/limits istemal na karein.

Password kahan set hota hai (code mein KABHI nahi):
  - Local test : .streamlit/secrets.toml  ->  app_password = "yourpassword"
  - Streamlit Cloud : app ke Settings -> Secrets  mein wahi line daalein

Behtar (hashed) tareeka bhi supported hai — neeche APP_PASSWORD_HASH dekhein.
"""

import hashlib
import hmac
import time

import streamlit as st

# Kitni der baad dobara login maanga jaye (seconds). Default: 8 ghante.
SESSION_TIMEOUT = 8 * 60 * 60


def _get_secret(name: str, default=None):
    """Secrets se value nikaalta hai (agar file/secrets na ho to crash nahi karta)."""
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


def _password_ok(entered: str) -> bool:
    """
    Constant-time comparison (timing attack se bachao).
    Do tareeke: plain password ya SHA-256 hash (hash zyada mehfooz).
    """
    hashed = _get_secret("app_password_hash")
    if hashed:
        entered_hash = hashlib.sha256(entered.encode()).hexdigest()
        return hmac.compare_digest(entered_hash, str(hashed))

    plain = _get_secret("app_password")
    if plain:
        return hmac.compare_digest(entered, str(plain))

    # Koi password set hi nahi (local dev) — gate off, lekin warning.
    return None  # None matlab "koi password configure nahi"


def require_login() -> None:
    """
    App ke shuru mein call karein. Agar login zaroori ho aur user logged-in
    na ho, to login form dikha kar app ROK deta hai (st.stop()).
    """
    # Pehle se logged in aur session abhi valid?
    if st.session_state.get("authed"):
        if time.time() - st.session_state.get("auth_time", 0) < SESSION_TIMEOUT:
            return
        # session expire ho gaya
        st.session_state["authed"] = False

    # Kya password configure hai?
    configured = bool(_get_secret("app_password") or _get_secret("app_password_hash"))
    if not configured:
        # Local dev: gate off. Ek halki warning taake deploy se pehle set karna yaad rahe.
        st.session_state["authed"] = True
        st.session_state["auth_time"] = time.time()
        st.session_state["_no_pw_warning"] = True
        return

    # ---- Login form ----
    st.markdown("## 🔒 AI Trading Assistant — Login")
    st.caption("Yeh app private hai. Aage barhne ke liye password daalein.")
    with st.form("login_form"):
        pw = st.text_input("Password", type="password")
        ok = st.form_submit_button("🔓 Login", type="primary")
    if ok:
        result = _password_ok(pw)
        if result:
            st.session_state["authed"] = True
            st.session_state["auth_time"] = time.time()
            st.session_state["login_attempts"] = 0
            st.rerun()
        else:
            attempts = st.session_state.get("login_attempts", 0) + 1
            st.session_state["login_attempts"] = attempts
            # Basic brute-force slowdown
            if attempts >= 3:
                st.error("Bar bar ghalat password. Thora intezaar karein.")
                time.sleep(min(attempts, 8))
            else:
                st.error("Ghalat password. Dobara koshish karein.")
    st.stop()   # login se aage kuch bhi render na ho


def logout_button() -> None:
    """Sidebar mein logout button (login on hone par)."""
    if st.session_state.get("authed") and (
        _get_secret("app_password") or _get_secret("app_password_hash")
    ):
        if st.sidebar.button("🔒 Logout"):
            st.session_state["authed"] = False
            st.rerun()


def hash_password(plain: str) -> str:
    """Helper: password ka SHA-256 hash banata hai (secrets mein daalne ke liye)."""
    return hashlib.sha256(plain.encode()).hexdigest()
