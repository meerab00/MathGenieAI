
import streamlit as st
from utils.groq_client import get_groq_response, get_groq_vision_response
from utils.history_manager import save_chat, clear_all_history
from utils.formula_sheet import FORMULA_SHEET
from utils.system_prompt import build_system_prompt
from utils.math_keyboard import MATH_SYMBOLS
import base64

# ───────────────────────────────
# 1. PAGE CONFIG (App ka title + icon)
# ───────────────────────────────
st.set_page_config(
    page_title="MathGenie AI",
    page_icon="🧞",
    layout="wide"
)

# ───────────────────────────────
# 2. SESSION STATE (data store karne ke liye)
# ───────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []   # chat history

if "text" not in st.session_state:
    st.session_state.text = ""       # keyboard input store

if "groq_key" not in st.session_state:
    st.session_state.groq_key = ""

# ───────────────────────────────
# 3. SIDEBAR (settings panel)
# ───────────────────────────────
with st.sidebar:
    st.title("🧞 MathGenie AI")

    # API KEY input
    api_key = st.text_input("Groq API Key", type="password")
    if api_key:
        st.session_state.groq_key = api_key

    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        clear_all_history()

# ───────────────────────────────
# 4. TITLE
# ───────────────────────────────
st.title("🧞 MathGenie AI (ChatGPT Style)")

# ───────────────────────────────
# 5. CHAT DISPLAY (purani messages show karna)
# ───────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ───────────────────────────────
# 6. KEYBOARD (symbol add karega input me)
# ───────────────────────────────
with st.expander("⌨️ Math Keyboard"):

    # STEP: ensure storage exists
    if "text" not in st.session_state:
        st.session_state.text = ""

    cols = st.columns(8)

    # STEP: all symbols ek list me convert
    symbols = []
    for s in MATH_SYMBOLS.values():
        symbols.extend(s)

    # STEP: button click = symbol add
    for i, sym in enumerate(symbols):
        if cols[i % 8].button(sym, key=f"kb_{i}"):
            st.session_state.text += sym   # yahan input me add ho raha hai

# ───────────────────────────────
# 7. INPUT SECTION (stable version)
# ───────────────────────────────

# STEP: input box (keyboard + typing dono yahan store honge)
question = st.text_input(
    "Type your math question",
    value=st.session_state.text
)

# STEP: sync session state
st.session_state.text = question

# ───────────────────────────────
# 8. IMAGE UPLOAD (optional vision input)
# ───────────────────────────────
uploaded_file = st.file_uploader("📷 Upload Image", type=["jpg","png","jpeg"])
camera_image = st.camera_input("📸 Take Photo")

# image bytes store
img_bytes = None

if uploaded_file:
    img_bytes = uploaded_file.read()
elif camera_image:
    img_bytes = camera_image.getvalue()

# ───────────────────────────────
# 9. SEND / PROCESS (AI call)
# ───────────────────────────────
if question or img_bytes:

    # STEP: user message save
    st.session_state.messages.append({
        "role": "user",
        "content": question if question else "Image Question"
    })

    with st.chat_message("assistant"):
        with st.spinner("Solving..."):

            try:
                # STEP: system prompt load
                system_prompt = build_system_prompt("General")

                history = st.session_state.messages[-8:]

                # STEP: image vs text decision
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

                # STEP: safety convert to string
                response = str(response)

                # STEP: show answer
                st.markdown(response)

                # STEP: save assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

                # STEP: save history
                save_chat(question, st.session_state.messages)

                # STEP: clear keyboard input
                st.session_state.text = ""

            except Exception as e:
                st.error(f"Error: {e}")
