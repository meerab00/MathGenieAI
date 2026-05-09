
import streamlit as st
from utils.groq_client import get_groq_response, get_groq_vision_response
from utils.history_manager import save_chat, clear_all_history
from utils.formula_sheet import FORMULA_SHEET
from utils.system_prompt import build_system_prompt
from utils.math_keyboard import MATH_SYMBOLS
import base64

# ── CONFIG ──
st.set_page_config(
    page_title="MathGenie AI",
    page_icon="🧞",
    layout="wide"
)

# ── SESSION ──
if "messages" not in st.session_state:
    st.session_state.messages = []

if "text" not in st.session_state:
    st.session_state.text = ""

if "groq_key" not in st.session_state:
    st.session_state.groq_key = ""

# ── SIDEBAR ──
with st.sidebar:
    st.title("🧞 MathGenie AI")

    api_key = st.text_input("Groq API Key", type="password")
    if api_key:
        st.session_state.groq_key = api_key

    if st.button("Clear Chat"):
        st.session_state.messages = []
        clear_all_history()

# ── TITLE ──
st.title("🧞 MathGenie AI")

# ── CHAT DISPLAY ──
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── KEYBOARD (SIMPLE) ──
with st.expander("⌨️ Math Keyboard"):

    cols = st.columns(8)

    symbols = []
    for s in MATH_SYMBOLS.values():
        symbols.extend(s)

    for i, sym in enumerate(symbols):
        if cols[i % 8].button(sym, key=f"kb_{i}"):
            st.session_state.text += sym

# ── INPUT ──
uploaded_file = st.file_uploader("📷 Upload Image", type=["jpg","png","jpeg"])

user_input = st.text_input(
    "Type your question",
    value=st.session_state.text
)

st.session_state.text = user_input

# ── PROCESS ──
if user_input or uploaded_file:

    if not st.session_state.groq_key:
        st.error("Enter API key first")
        st.stop()

    img_bytes = None

    if uploaded_file:
        img_bytes = uploaded_file.read()

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("assistant"):

        try:
            system_prompt = build_system_prompt("General")

            history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[-6:]
            ]

            if img_bytes:
                img_b64 = base64.b64encode(img_bytes).decode()

                response = get_groq_vision_response(
                    st.session_state.groq_key,
                    system_prompt,
                    user_input,
                    img_b64
                )
            else:
                response = get_groq_response(
                    st.session_state.groq_key,
                    system_prompt,
                    history
                )

            st.markdown(str(response))

            st.session_state.messages.append({
                "role": "assistant",
                "content": str(response)
            })

            save_chat(user_input, st.session_state.messages)

        except Exception as e:
            st.error(f"Error: {e}")
