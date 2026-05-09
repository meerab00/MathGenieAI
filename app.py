
import streamlit as st
from utils.groq_client import get_groq_response, get_groq_vision_response
import base64

# ── CONFIG ──
st.set_page_config(page_title="MathGenie AI", page_icon="🧞")

# ── SESSION ──
if "messages" not in st.session_state:
    st.session_state.messages = []

if "text" not in st.session_state:
    st.session_state.text = ""

if "groq_key" not in st.session_state:
    st.session_state.groq_key = ""

# ── TITLE ──
st.title("🧞 MathGenie AI")

# ── API KEY ──
api_key = st.text_input("Enter Groq API Key", type="password")
if api_key:
    st.session_state.groq_key = api_key

# ── CHAT DISPLAY ──
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── KEYBOARD ──
symbols = ["+", "-", "*", "/", "=", "^2", "(", ")"]

st.write("⌨️ Keyboard")
cols = st.columns(5)

for i, s in enumerate(symbols):
    if cols[i % 5].button(s, key=f"k{i}"):
        st.session_state.text += s

# ── INPUT ──
user_input = st.text_input("Type your question", value=st.session_state.text)
st.session_state.text = user_input

uploaded_file = st.file_uploader("📷 Upload Image", type=["jpg","png","jpeg"])

# ── SEND BUTTON ──
send = st.button("Solve")

# ── PROCESS ──
if send and user_input:

    if not st.session_state.groq_key:
        st.error("Please enter API key")
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
            history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[-6:]
            ]

            if img_bytes:
                img_b64 = base64.b64encode(img_bytes).decode()

                response = get_groq_vision_response(
                    st.session_state.groq_key,
                    "You are a math tutor",
                    user_input,
                    img_b64
                )
            else:
                response = get_groq_response(
                    st.session_state.groq_key,
                    "You are a math tutor",
                    history
                )

            st.markdown(response)

            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

        except Exception as e:
            st.error(f"Error: {e}")
