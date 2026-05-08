
import streamlit as st
from utils.groq_client import get_groq_response, get_groq_vision_response
from utils.practice_gen import generate_practice_questions
from utils.history_manager import save_chat, load_chats, clear_all_history
from utils.formula_sheet import FORMULA_SHEET
from utils.system_prompt import build_system_prompt
from utils.math_keyboard import MATH_SYMBOLS
import base64

# ── CONFIG ─────────────────────────────────────────────
st.set_page_config(
    page_title="MathGenie AI",
    page_icon="🧞",
    layout="wide"
)

# ── SESSION STATE ──────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "topic" not in st.session_state:
    st.session_state.topic = "General"

if "groq_key" not in st.session_state:
    try:
        st.session_state.groq_key = st.secrets["GROQ_API_KEY"]
    except:
        st.session_state.groq_key = ""

# ── SIDEBAR ────────────────────────────────────────────
with st.sidebar:

    st.title("🧞 MathGenie AI")

    api_key = st.text_input(
        "Groq API Key",
        type="password",
        value=st.session_state.groq_key
    )

    if api_key:
        st.session_state.groq_key = api_key
        st.success("Key Saved")

    st.divider()

    st.session_state.topic = st.selectbox(
        "Select Topic",
        [
            "General",
            "Calculus",
            "Algebra",
            "Statistics",
            "Optimization Theory",
            "Fuzzy Set Theory",
            "Linear Algebra",
            "ODE / PDE",
            "Number Theory"
        ]
    )

    st.divider()

    st.subheader("📐 Formula Sheet")

    for subject, formulas in FORMULA_SHEET.items():
        with st.expander(subject):
            for f in formulas:
                st.code(f)

    st.divider()

    st.subheader("📝 Practice Questions")

    prac_topic = st.selectbox(
        "Choose Topic",
        ["Calculus", "Algebra", "Statistics", "Optimization", "Fuzzy Sets"]
    )

    if st.button("Generate Questions"):

        if not st.session_state.groq_key:
            st.error("Enter API Key first")

        else:
            with st.spinner("Generating..."):
                qs = generate_practice_questions(
                    st.session_state.groq_key,
                    prac_topic
                )
                st.session_state.practice_questions = qs

    if "practice_questions" in st.session_state:
        for i, q in enumerate(st.session_state.practice_questions):
            if st.button(f"Q{i+1}"):
                st.session_state.prefill_question = q

    st.divider()

    st.subheader("💬 History")

    history = load_chats()

    if history:
        for i, chat in enumerate(history[:5]):
            if st.button(chat["question"][:30], key=f"h{i}"):
                st.session_state.messages = chat["messages"]
                st.rerun()

    if st.button("Clear History"):
        clear_all_history()
        st.success("Cleared")

    if st.button("New Chat"):
        st.session_state.messages = []
        st.rerun()

# ── HEADER ─────────────────────────────────────────────
st.title("🧞 MathGenie AI")
st.write("Your AI Math Tutor")

# ── CHAT DISPLAY ───────────────────────────────────────
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])

        if msg.get("image"):
            st.image(msg["image"], width=250)

# ── KEYBOARD ───────────────────────────────────────────
with st.expander("⌨️ Math Keyboard"):

    for section, symbols in MATH_SYMBOLS.items():

        st.write(section)

        cols = st.columns(min(len(symbols), 10))

        for i, (col, sym) in enumerate(zip(cols, symbols)):
            with col:
                if st.button(sym, key=f"{section}_{i}"):
                    st.session_state.kb_insert = sym

    if "kb_insert" in st.session_state:
        st.info(f"Copied: {st.session_state.kb_insert}")

# ── INPUT ──────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Upload Image",
    type=["jpg", "jpeg", "png", "webp"]
)

prefill = st.session_state.pop("prefill_question", "")

user_input = st.chat_input("Type your math question...")

question = user_input or prefill

# ── PROCESS ────────────────────────────────────────────
if question or uploaded_file:

    if not st.session_state.groq_key:
        st.error("Enter Groq API Key")
        st.stop()

    display_q = question or "Solve this image"

    user_msg = {
        "role": "user",
        "content": display_q
    }

    img_bytes = None

    if uploaded_file:
        img_bytes = uploaded_file.read()
        user_msg["image"] = img_bytes

    st.session_state.messages.append(user_msg)

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:
                system_prompt = build_system_prompt(st.session_state.topic)

                history_for_api = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[-8:]
                    if isinstance(m.get("content"), str)
                ]

                if img_bytes:
                    img_b64 = base64.b64encode(img_bytes).decode()

                    response = get_groq_vision_response(
                        st.session_state.groq_key,
                        system_prompt,
                        question or "Solve step by step",
                        img_b64
                    )
                else:
                    response = get_groq_response(
                        st.session_state.groq_key,
                        system_prompt,
                        history_for_api
                    )

                if not response:
                    st.error("No response from AI")
                    st.stop()

                st.markdown(response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

                save_chat(display_q, st.session_state.messages)

            except Exception as e:
                st.error(f"Error: {e}")

    st.rerun()
