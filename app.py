"""TOME landing page and authentication entry point."""

from __future__ import annotations

import streamlit as st

from auth import authenticate, create_user


ACCENT = "#b0e101"
MUTED = "#9ca3af"

st.set_page_config(
    page_title="TOME | Landing",
    page_icon="\U0001f4d6",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
    :root {{ --accent: {ACCENT}; }}
    .stApp {{
        background: #03080a;
        color: #f5f5f0;
        font-family: 'Manrope', sans-serif;
    }}
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarNav"], [data-testid="stToolbar"],
    [data-testid="stDecoration"], [data-testid="stStatusWidget"],
    [data-testid="stAppDeployButton"], [data-testid="stDeployButton"],
    [data-testid="stMainMenu"], [data-testid="stHeaderActionElements"],
    #MainMenu {{
        display: none !important;
    }}
    header[data-testid="stHeader"] {{
        height: 0;
        min-height: 0;
        background: transparent;
        position: absolute;
        top: 0;
        overflow: hidden;
    }}
    header[data-testid="stHeader"] * {{ display: none !important; }}
    .block-container {{
        max-width: 1200px;
        margin: 0 auto;
        padding-top: 0 !important;
    }}
    .landing-brand {{
        font-size: clamp(3.6rem, 8vw, 7rem);
        font-weight: 800;
        letter-spacing: -.09em;
        color: var(--accent);
        margin: 0;
    }}
    .landing-subtitle {{ color: #c3c8cb; font-size: 1.18rem; max-width: 620px; }}
    .eyebrow {{
        color: var(--accent);
        font-family: 'DM Mono', monospace;
        font-size: .72rem;
        letter-spacing: .16em;
        text-transform: uppercase;
    }}
    .hero-title {{
        font-size: clamp(2.6rem, 6vw, 5.6rem);
        font-weight: 800;
        letter-spacing: -.08em;
        line-height: .96;
        margin: .55rem 0 1rem;
    }}
    .hero-copy {{ color: {MUTED}; font-size: 1.05rem; max-width: 650px; line-height: 1.7; }}
    .auth-card {{ max-width: 470px; margin: 3rem auto 0; }}
    .stButton > button {{
        border-radius: 9px;
        border: 1px solid var(--accent);
        color: #10120b;
        background: var(--accent);
        font-weight: 700;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="landing-brand">TOME.</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="landing-subtitle">Your private reading room for PDFs, summaries, and meaningful conversations.</div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="eyebrow">A calmer way to read</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-title">Your PDFs.<br><span style="color:#b0e101">Understood.</span></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero-copy">TOME turns long documents into clear summaries and useful conversations. Create a free account to open your private reading room.</div>',
    unsafe_allow_html=True,
)
st.write("")

st.markdown('<div class="auth-card">', unsafe_allow_html=True)
login_tab, signup_tab = st.tabs(["Sign in", "Create account"])
with login_tab:
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Enter TOME", type="primary", use_container_width=True)
    if submitted:
        if not email or not password:
            st.error("Enter both your email and password.")
        else:
            success, message, name = authenticate(email, password)
            if success:
                st.session_state.authenticated = True
                st.session_state.user_name = name
                st.session_state.user_email = email.strip().lower()
                st.switch_page("pages/home.py")
            else:
                st.error(message)

with signup_tab:
    with st.form("signup_form"):
        name = st.text_input("Name", placeholder="Your name")
        email = st.text_input("Email", placeholder="you@example.com", key="signup_email")
        password = st.text_input("Password", type="password", help="Use at least 8 characters.")
        confirm_password = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Create my account", type="primary", use_container_width=True)
    if submitted:
        if not name.strip() or not email.strip() or len(password) < 8:
            st.error("Enter your name, a valid email, and a password of at least 8 characters.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            success, message = create_user(name, email, password)
            if success:
                st.success(message)
            else:
                st.error(message)
st.markdown("</div>", unsafe_allow_html=True)
