"""TOME signed-in workspace."""

from __future__ import annotations

import os
import re
from collections import Counter
from io import BytesIO
from typing import Any

import requests
import streamlit as st
from pypdf import PdfReader

from auth import get_document, list_documents, save_document


st.set_page_config(
    page_title="TOME | Reading room",
    page_icon="\U0001f4d6",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --accent: #b0e101;
        --accent-deep: #8fb800;
        --surface: #0b1310;
        --border: #1f2a22;
    }
    .stApp { background: #03080a; color: #f5f5f0; }
    [data-testid="stSidebarNav"],
    [data-testid="stDecoration"], [data-testid="stStatusWidget"],
    [data-testid="stAppDeployButton"], [data-testid="stDeployButton"],
    [data-testid="stMainMenu"], [data-testid="stHeaderActionElements"],
    #MainMenu {
        display: none !important;
    }
    header[data-testid="stHeader"] {
        height: 25px;
        min-height: 25px;
        background: #03080a;
        position: relative;
        top: 0;
        z-index: 999;
    }
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        visibility: visible !important;
        z-index: 1002 !important;
    }

    /* ================= SIDEBAR ================= */
    [data-testid="stSidebar"] {
        background: #03080a;
        border-right: 1px solid #172016;
        width: 290px;
    }
    [data-testid="stSidebarHeader"] {
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        overflow: visible;
    }
    [data-testid="stSidebarHeader"] button {
        position: absolute;
        top: 4px;
        right: 8px;
        z-index: 5;
    }
    [data-testid="stSidebarUserContent"] {
        padding: 0.6rem 0.6rem 0.6rem 0.6rem !important;  /* bottom space for fixed Sign out */
    }
    [data-testid="stSidebarContent"] { overflow-y: auto !important; }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .6rem !important; }

    .side-brand { font-size: 1.8rem; font-weight: 400; margin: 0 0 .4rem; }
    .eyebrow {
        color: var(--accent);
        font-family: monospace;
        font-size: .72rem;
        letter-spacing: .16em;
        text-transform: uppercase;
        margin-top: .4rem;
        margin-bottom : .4rem;
    }
    .provider-status {
        border: 1px solid #172016;
        border-radius: 12px;
        padding: .7rem 1rem;
    }

    /* Library items: normal (dark) blocks, not fluorescent */
    [data-testid="stSidebar"] [class*="st-key-library_"] button {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        color: #e5e7eb !important;
        font-weight: 500;
    }
    [data-testid="stSidebar"] [class*="st-key-library_"] button > div {
        justify-content: flex-start;
    }
    [data-testid="stSidebar"] [class*="st-key-library_"] button p {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    [data-testid="stSidebar"] [class*="st-key-library_"] button:hover,
    [data-testid="stSidebar"] [class*="st-key-library_"] button:focus:not(:active),
    [data-testid="stSidebar"] [class*="st-key-library_"] button:active {
        background: #121d17 !important;
        border-color: var(--accent) !important;
        color: #ffffff !important;
    }

    /* Sign out: red, pinned to the bottom of the sidebar */
    .st-key-signout {
        position: fixed;
        bottom: 10px;
        left: 1.5rem;
        width: calc(250px - 3rem);
        z-index: 1001;
    }
    [data-testid="stSidebar"][aria-expanded="false"] .st-key-signout { display: none !important; }
    [data-testid="stSidebar"] .st-key-signout button {
        background: #dc2626 !important;
        border: 1px solid #dc2626 !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .st-key-signout button:hover,
    [data-testid="stSidebar"] .st-key-signout button:focus:not(:active),
    [data-testid="stSidebar"] .st-key-signout button:active {
        background: #b91c1c !important;
        border-color: #b91c1c !important;
        color: #ffffff !important;
    }
    /* ================= END SIDEBAR ================= */

    [data-testid="stAppViewContainer"],
    [data-testid="stMainBlockContainer"],
    .block-container {
        padding-top: .5rem !important;
        margin-top: 0 !important;
    }
    .block-container { padding-bottom: 120px !important; }

    .hero-title {
        font-size: clamp(2.6rem, 6vw, 5.6rem);
        font-weight: 800;
        letter-spacing: -.08em;
        line-height: .96;
        margin: 0 0 1rem;
    }
    .section-title {
        font-weight: 600;
        font-size: 1.05rem;
        color: #e5e7eb;
        margin: .4rem 0 1rem;
    }
    .metric {
        background: #03080a;
        border: 1px solid #172016;
        border-radius: 12px;
        padding: 1rem 1.1rem;
    }
    .metric-value { font-size: 1.45rem; font-weight: 700; }
    .metric-label { color: #9ca3af; font-family: monospace; font-size: .67rem; }
    .empty-state {
        border: 1px dashed #3a4145;
        border-radius: 18px;
        padding: 4rem 2rem;
        text-align: center;
        color: #9ca3af;
    }
    div[data-testid="stFileUploader"] {
        background: #03080a;
        border: 1px solid #172016;
        border-radius: 14px;
        padding: .5rem;
    }

    /* Buttons: fluorescent, and a DEEPER green on hover (never black) */
    .stButton > button {
        border-radius: 9px;
        border: 1px solid var(--accent);
        color: #10120b;
        background: var(--accent);
        font-weight: 700;
    }
    .stButton > button p { color: inherit !important; }
    .stButton > button:hover,
    .stButton > button:focus:not(:active),
    .stButton > button:active {
        background: var(--accent-deep) !important;
        border-color: var(--accent-deep) !important;
        color: #10120b !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 1.6rem; border-bottom: 1px solid #172016; }
    .stTabs [data-baseweb="tab"] p { color: #9ca3af; font-weight: 600; }
    .stTabs [aria-selected="true"] p { color: var(--accent) !important; }
    .stTabs [data-baseweb="tab-highlight"] { background-color: var(--accent) !important; }

    /* Chat messages */
    .stChatMessage {
        background: var(--surface);
        border: 1px solid #172016;
        border-radius: 14px;
    }

    /* Chat input (pinned natively by Streamlit, styled here) */
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div {
        background: #03080a !important;
    }
    [data-testid="stChatInput"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    [data-testid="stChatInput"] > div {
        background: var(--surface) !important;
        border: 1px solid #26332a !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, .45);
        transition: border-color .15s, box-shadow .15s;
    }
    [data-testid="stChatInput"] > div:focus-within {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent), 0 8px 30px rgba(176, 225, 1, .12);
    }
    [data-testid="stChatInput"] [data-baseweb="textarea"],
    [data-testid="stChatInput"] [data-baseweb="base-input"] {
        background: transparent !important;
        border: none !important;
    }
    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: #f5f5f0 !important;
        font-size: 1rem !important;
        min-height: 56px !important;
        padding: 1rem .5rem !important;
    }
    [data-testid="stChatInput"] textarea::placeholder { color: #6b7780 !important; }
    [data-testid="stChatInput"] button {
        background: var(--accent) !important;
        color: #10120b !important;
        border-radius: 10px !important;
    }
    [data-testid="stChatInput"] button:hover { background: var(--accent-deep) !important; }
    [data-testid="stChatInput"] button svg { fill: #10120b !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


def extract_pdf(uploaded_file: Any) -> tuple[str, int]:
    reader = PdfReader(BytesIO(uploaded_file.getvalue()))
    pages = [(page.extract_text() or "").strip() for page in reader.pages]
    return "\n\n".join(page for page in pages if page), len(reader.pages)


def split_text(text: str, size: int = 1400, overlap: int = 180) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    return [cleaned[start:start + size] for start in range(0, len(cleaned), size - overlap)]


def local_summary(text: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text).strip())
    sentences = [sentence for sentence in sentences if len(sentence.split()) > 5]
    if not sentences:
        return "TOME could not find extractable text in this PDF. It may be a scanned document."
    words = re.findall(r"[A-Za-z][A-Za-z'-]{2,}", text.lower())
    stop_words = {
        "about", "after", "again", "also", "been", "being", "from", "have",
        "into", "more", "most", "other", "over", "such", "than", "that",
        "their", "there", "these", "they", "this", "through", "with", "would",
    }
    common = [word for word, count in Counter(words).most_common(10) if word not in stop_words and count > 1]
    return f"**Overview**\n\n{' '.join(sentences[:3])}\n\n**Key themes**\n\nThis document repeatedly focuses on {', '.join(common[:5]) if common else 'the document main ideas'}."


def relevant_context(question: str, chunks: list[str], limit: int = 3) -> str:
    query_words = set(re.findall(r"[a-zA-Z]{3,}", question.lower()))
    ranked = sorted(
        chunks,
        key=lambda chunk: len(query_words & set(re.findall(r"[a-zA-Z]{3,}", chunk.lower()))),
        reverse=True,
    )
    return "\n\n".join(ranked[:limit])


PROVIDER_CONFIGS = {
    "OpenAI": ("https://api.openai.com/v1/models", "bearer"),
    "Claude": ("https://api.anthropic.com/v1/models", "anthropic"),
    "Grok": ("https://api.x.ai/v1/models", "bearer"),
    "OpenRouter": ("https://openrouter.ai/api/v1/models", "bearer"),
    "NVIDIA": ("https://integrate.api.nvidia.com/v1/models", "bearer"),
    "DeepSeek": ("https://api.deepseek.com/models", "bearer"),
    "Kimi": ("https://api.moonshot.cn/v1/models", "bearer"),
    "MiniMax": ("https://api.minimax.chat/v1/models", "bearer"),
}


def validate_provider(provider: str, api_key: str, custom_name: str = "") -> tuple[bool, str]:
    if not api_key.strip():
        return False, "Enter an API key."
    if provider == "Others":
        if not custom_name.strip():
            return False, "Enter the provider name."
        return True, f"{custom_name.strip()} API key saved for this session."

    endpoint, auth_type = PROVIDER_CONFIGS[provider]
    headers = {"Authorization": f"Bearer {api_key.strip()}"}
    if auth_type == "anthropic":
        headers = {"x-api-key": api_key.strip(), "anthropic-version": "2023-06-01"}
    try:
        response = requests.get(endpoint, headers=headers, timeout=12)
        if response.status_code in (200, 201):
            return True, f"{provider} API key verified successfully."
        if response.status_code in (401, 403):
            return False, f"{provider} rejected the API key."
        return False, f"{provider} returned HTTP {response.status_code}. The key could not be verified."
    except requests.RequestException as exc:
        return False, f"Could not reach {provider}: {exc}"


PROVIDER_DEFAULT_MODELS = {
    "OpenAI": ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"],
    "Claude": ["claude-3-5-haiku-latest", "claude-3-7-sonnet-latest", "claude-sonnet-4-20250514"],
    "Grok": ["grok-3-mini", "grok-3", "grok-2-latest"],
    "OpenRouter": [
        "openai/gpt-4o-mini",
        "anthropic/claude-3.5-haiku",
        "google/gemini-2.0-flash-001",
        "meta-llama/llama-3.3-70b-instruct",
        "deepseek/deepseek-chat",
    ],
    "NVIDIA": ["meta/llama-3.1-70b-instruct", "deepseek-ai/deepseek-r1"],
    "DeepSeek": ["deepseek-chat", "deepseek-reasoner"],
    "Kimi": ["moonshot-v1-8k", "moonshot-v1-32k"],
    "MiniMax": ["MiniMax-Text-01"],
}


def fetch_openrouter_models(api_key: str) -> list[str]:
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {api_key.strip()}"},
            timeout=12,
        )
        if response.status_code == 200:
            models = response.json().get("data", [])
            return [model["id"] for model in models if model.get("id")][:100]
    except (requests.RequestException, ValueError):
        pass
    return PROVIDER_DEFAULT_MODELS["OpenRouter"]


def verify_model_request(provider: str, api_key: str, model: str) -> tuple[bool, str]:
    endpoint = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key.strip()}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
        "max_tokens": 8,
    }
    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            return True, f"{provider} model verified successfully."
        detail = ""
        try:
            detail = response.json().get("error", {}).get("message", "")
        except ValueError:
            detail = response.text[:180]
        return False, detail or f"{provider} returned HTTP {response.status_code}."
    except requests.RequestException as exc:
        return False, f"Could not reach {provider}: {exc}"


@st.dialog("Connect an intelligence provider", width="small")
def provider_dialog() -> None:
    st.markdown("Choose a provider. The API key is masked and is kept only in this session.")
    provider = st.selectbox("Provider", list(PROVIDER_CONFIGS.keys()) + ["Others"])
    custom_name = st.text_input("Provider name", placeholder="Example: Together AI") if provider == "Others" else ""
    api_key = st.text_input("API key", type="password", placeholder="Paste your API key", key="provider_api_key")
    if provider == "Others":
        model = st.text_input("Model ID", placeholder="Example: provider/model-name")
    elif provider == "OpenRouter" and api_key.strip():
        openrouter_models = fetch_openrouter_models(api_key)
        model = st.selectbox("Model", openrouter_models)
    else:
        model = st.selectbox("Model", PROVIDER_DEFAULT_MODELS.get(provider, []))
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Verify & save", type="primary", use_container_width=True):
            success, message = validate_provider(provider, api_key, custom_name)
            if success:
                model_verified = True
                model_message = ""
                if provider == "OpenRouter":
                    model_verified, model_message = verify_model_request(provider, api_key, model)
                if not model_verified:
                    st.session_state.provider_verified = False
                    st.error(model_message)
                    return
                st.session_state.provider_name = custom_name.strip() if provider == "Others" else provider
                st.session_state.provider_key = api_key.strip()
                st.session_state.provider_model = model
                st.session_state.provider_verified = True
                st.success(model_message or message)
            else:
                st.session_state.provider_verified = False
                st.error(message)
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


def ask_openai(prompt: str, context: str, api_key: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=os.getenv("TOME_MODEL", "gpt-4o-mini"),
        instructions=(
            "You are TOME, a precise PDF research assistant. Answer only from the "
            "provided context. If the context does not contain the answer, say so "
            "clearly. Keep answers concise and use bullets when helpful."
        ),
        input=f"PDF CONTEXT:\n{context}\n\nUSER QUESTION:\n{prompt}",
    )
    return response.output_text


def ask_openrouter(prompt: str, context: str, api_key: str, model: str) -> str:
    import requests

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are TOME, a precise PDF research assistant. Answer only from "
                        "the provided context. If the context does not contain the answer, "
                        "say so clearly."
                    ),
                },
                {"role": "user", "content": f"PDF CONTEXT:\n{context}\n\nUSER QUESTION:\n{prompt}"},
            ],
        },
        timeout=60,
    )
    if response.status_code != 200:
        detail = response.text[:300]
        raise RuntimeError(f"OpenRouter returned HTTP {response.status_code}: {detail}")
    return response.json()["choices"][0]["message"]["content"]


def open_document(document_id: Any) -> None:
    loaded = get_document(st.session_state.user_email, document_id)
    if loaded:
        name, text, summary, page_count = loaded
        st.session_state.document_name = name
        st.session_state.document_text = text
        st.session_state.summary = summary
        st.session_state.chunks = split_text(text)
        st.session_state.page_count = page_count
        st.session_state.messages = []
        st.session_state.active_view = "thread"
        st.rerun()


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if not st.session_state.authenticated:
    st.switch_page("app.py")
    st.stop()

for key, value in {
    "messages": [],
    "document_text": "",
    "document_name": "",
    "chunks": [],
    "active_view": "thread",
    "provider_verified": False,
    "provider_name": "",
    "provider_key": "",
    "provider_model": "",
    "summary": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------------------------------------------------------- SIDEBAR
# Order: New Thread -> Extract data -> Intelligence -> My Library -> Library (last 5) -> Sign out
with st.sidebar:
    st.markdown('<div class="side-brand">TOME.</div>', unsafe_allow_html=True)

    if st.button("＋  New Thread", key="nav_new", use_container_width=True):
        st.session_state.active_view = "thread"
        st.session_state.document_text = ""
        st.session_state.document_name = ""
        st.session_state.chunks = []
        st.session_state.messages = []
        st.session_state.summary = ""
        st.rerun()

    if st.button("▦  Extract data", key="nav_extract", use_container_width=True):
        st.session_state.active_view = "extract"
        st.rerun()

    st.markdown('<div class="eyebrow">Intelligence</div>', unsafe_allow_html=True)
    if st.session_state.provider_verified:
        st.markdown(
            f'<div class="provider-status">✓ <strong>{st.session_state.provider_name}</strong><br>'
            f'<span style="color:#9ca3af">{st.session_state.provider_model}</span><br>'
            f'<span style="color:#9ca3af">API key verified</span></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="provider-status">No provider selected</div>', unsafe_allow_html=True)
    if st.button("Configure intelligence", key="nav_config", use_container_width=True):
        provider_dialog()

    if st.button("▥  My Library", key="nav_library", use_container_width=True):
        st.session_state.active_view = "library"
        st.rerun()

    st.markdown("**Library**")
    library = list_documents(st.session_state.user_email)
    for document_id, name, _, page_count, _ in library[:5]:
        if st.button(name, key=f"library_{document_id}", use_container_width=True):
            open_document(document_id)

    # Pinned to the bottom of the sidebar and coloured red via CSS (.st-key-signout)
    if st.button("Sign out", key="signout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.pop("document_text", None)
        st.session_state.pop("document_name", None)
        st.session_state.pop("messages", None)
        st.switch_page("app.py")

# ---------------------------------------------------------------- MAIN PAGE
if st.session_state.active_view == "library":
    st.markdown('<div class="hero-title" style="font-size:3.2rem">My Library</div>', unsafe_allow_html=True)
    library = list_documents(st.session_state.user_email)
    if not library:
        st.markdown('<div class="empty-state"><h3>No PDFs yet</h3><p>Open a new thread and upload a document.</p></div>', unsafe_allow_html=True)
    for document_id, name, summary, page_count, updated_at in library:
        with st.container(border=True):
            st.markdown(f"### {name}")
            st.caption(f"{page_count} pages · Updated {updated_at}")
            if st.button("Open document", key=f"open_{document_id}"):
                open_document(document_id)
    st.stop()

if st.session_state.active_view == "extract":
    st.markdown('<div class="hero-title" style="font-size:3.2rem">Extracted data</div>', unsafe_allow_html=True)
    library = list_documents(st.session_state.user_email)
    if not library:
        st.markdown('<div class="empty-state"><h3>No extracted summaries</h3><p>Upload a PDF and TOME will add its summary here.</p></div>', unsafe_allow_html=True)
    for _, name, summary, _, _ in library:
        with st.container(border=True):
            st.markdown(f"### {name}")
            st.markdown(summary)
    st.stop()

st.markdown('<div class="hero-title" style="font-size:3.2rem">Meet your PDF<br><span style="color:#b0e101">halfway.</span></div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"], help="PDF files up to 200 MB")
if uploaded_file and uploaded_file.name != st.session_state.document_name:
    try:
        with st.spinner("Reading and summarizing your document..."):
            text, page_count = extract_pdf(uploaded_file)
            summary = local_summary(text)
            save_document(st.session_state.user_email, uploaded_file.name, text, summary, page_count)
        st.session_state.document_text = text
        st.session_state.document_name = uploaded_file.name
        st.session_state.chunks = split_text(text)
        st.session_state.page_count = page_count
        st.session_state.summary = summary
        st.session_state.messages = []
    except Exception as exc:
        st.error(f"Could not read this PDF: {exc}")

if not st.session_state.document_text:
    st.markdown(
        '<div class="empty-state"><div class="empty-icon">✦</div><h3>Your reading room is waiting.</h3><p>Upload a PDF to generate a summary and start a conversation.</p></div>',
        unsafe_allow_html=True,
    )
    st.stop()

text = st.session_state.document_text
page_count = st.session_state.get("page_count", "—")
word_count = len(text.split())
st.markdown(f"### {st.session_state.document_name}")
metric_cols = st.columns(3)
for column, value, label in zip(
    metric_cols,
    [page_count, f"{word_count:,}", len(st.session_state.chunks)],
    ["Pages", "Words", "Context blocks"],
):
    with column:
        st.markdown(
            f'<div class="metric"><div class="metric-value">{value}</div><div class="metric-label">{label}</div></div>',
            unsafe_allow_html=True,
        )

# Created at the top level (not inside a tab) so Streamlit pins it to the bottom natively.
question = st.chat_input("Ask anything about this document…")

chat_tab, summary_tab = st.tabs(["◎ Chat with PDF", "✦ Summary"])
with chat_tab:
    st.markdown('<div class="section-title">Ask anything about this document</div>', unsafe_allow_html=True)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        context = relevant_context(question, st.session_state.chunks)
        with st.chat_message("assistant"):
            try:
                if st.session_state.provider_verified and st.session_state.provider_name == "OpenRouter":
                    answer = ask_openrouter(
                        question,
                        context,
                        st.session_state.provider_key,
                        st.session_state.provider_model,
                    )
                elif st.session_state.provider_verified and st.session_state.provider_name == "OpenAI":
                    answer = ask_openai(
                        question,
                        context,
                        st.session_state.provider_key,
                    )
                else:
                    answer = f"Here are the relevant passages I found:\n\n{context}" if context else "I couldn't find extractable text relevant to that question."
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as exc:
                st.error(f"Chat failed: {exc}")

with summary_tab:
    st.markdown('<div class="section-title">The short version</div>', unsafe_allow_html=True)
    st.markdown(st.session_state.summary)