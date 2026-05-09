
import streamlit as st
from utils.groq_client import get_groq_response
from utils.history_manager import save_chat, clear_all_history
from utils.formula_sheet import FORMULA_SHEET
from utils.system_prompt import build_system_prompt

# ── CONFIG ─────────────────────────────────────
st.set_page_config(
    page_title="MathGenie AI",
    page_icon="🧞",
    layout="wide"
)

# ── SESSION STATE ─────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "topic" not in st.session_state:
    st.session_state.topic = "General"

if "groq_key" not in st.session_state:
    try:
        st.session_state.groq_key = st.secrets["GROQ_API_KEY"]
    except:
        st.session_state.groq_key = ""

# ── SIDEBAR ───────────────────────────────────
with st.sidebar:
    st.title("🧞 MathGenie AI")

    api_key = st.text_input("Groq API Key", type="password")

    if api_key:
        st.session_state.groq_key = api_key

    st.divider()

    st.session_state.topic = st.selectbox(
        "Topic",
        [
            "General","Calculus","Algebra","Statistics",
            "Optimization Theory","Fuzzy Set Theory",
            "Linear Algebra","ODE / PDE","Number Theory"
        ]
    )

    st.divider()

    st.subheader("📐 Formula Sheet")
    for subject, formulas in FORMULA_SHEET.items():
        with st.expander(subject):
            for f in formulas:
                st.code(f)

    st.divider()

    if st.button("Clear Chat"):
        st.session_state.messages = []
        clear_all_history()

# ── HEADER ────────────────────────────────────
st.title("🧞 MathGenie AI")
st.caption("ChatGPT-style Math Solver")

# ── CHAT DISPLAY ──────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── INPUT ─────────────────────────────────────
user_input = st.chat_input("Ask your math question...")

# ── PROCESS ───────────────────────────────────
if user_input:

    if not st.session_state.groq_key:
        st.error("Enter Groq API Key first")
        st.stop()

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("assistant"):
        with st.spinner("Solving..."):
            try:
                system_prompt = build_system_prompt(st.session_state.topic)

                history = st.session_state.messages[-8:]

                response = get_groq_response(
                    st.session_state.groq_key,
                    system_prompt,
                    history
                )

                response = getattr(response, "content", str(response))

                st.markdown(response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

                save_chat(st.session_state.messages)

            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()
