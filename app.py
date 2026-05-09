
import streamlit as st
from utils.groq_client import get_groq_response, get_groq_vision_response
from utils.history_manager import save_chat, load_chats, clear_all_history
from utils.formula_sheet import FORMULA_SHEET
from utils.system_prompt import build_system_prompt
from utils.math_keyboard import MATH_SYMBOLS
import base64

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

if "text" not in st.session_state:
    st.session_state.text = ""

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

# ── KEYBOARD ──────────────────────────────────
with st.expander("⌨️ Math Keyboard"):
    for section, symbols in MATH_SYMBOLS.items():
        st.write(section)
        cols = st.columns(min(len(symbols), 10))

        for i, (col, sym) in enumerate(zip(cols, symbols)):
            with col:
                if st.button(sym, key=f"{section}_{i}"):
                    st.session_state.text += sym

# ── INPUT SECTION (FIXED) ─────────────────────
uploaded_file = st.file_uploader(
    "📷 Upload Image",
    type=["jpg", "jpeg", "png", "webp"]
)

camera_image = st.camera_input("📸 Take Photo (optional)")

user_input = st.chat_input("Ask your math question...")

question = user_input or st.session_state.text

# ── PROCESS ───────────────────────────────────
if question or uploaded_file or camera_image:

    if not st.session_state.groq_key:
        st.error("Enter Groq API Key first")
        st.stop()

    img_bytes = None

    if uploaded_file:
        img_bytes = uploaded_file.read()

    elif camera_image:
        img_bytes = camera_image.getvalue()

    st.session_state.messages.append({
        "role": "user",
        "content": question if question else "Image Question"
    })

    with st.chat_message("assistant"):

        with st.spinner("Solving..."):

            try:
                system_prompt = build_system_prompt(st.session_state.topic)

                history = st.session_state.messages[-8:]

                if img_bytes:
                    img_b64 = base64.b64encode(img_bytes).decode()

                    response = get_groq_vision_response(
                        st.session_state.groq_key,
                        system_prompt,
                        question,
                        img_b64
                    )
                else:
                    response = get_groq_response(
                        st.session_state.groq_key,
                        system_prompt,
                        history
                    )

                if not isinstance(response, str):
                    response = str(response)

                st.markdown(response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

                save_chat(question, st.session_state.messages)

                # clear keyboard buffer
                st.session_state.text = ""

            except Exception as e:
                st.error(f"Error: {e}")
