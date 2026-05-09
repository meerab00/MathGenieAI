
import streamlit as st
from utils.groq_client import get_groq_response, get_groq_vision_response
from utils.practice_gen import generate_practice_questions
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

if "user_text" not in st.session_state:
    st.session_state.user_text = ""

# ── SIDEBAR ────────────────────────────────────
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

    st.subheader("📝 Practice")

    prac_topic = st.selectbox(
        "Choose Topic",
        ["Calculus","Algebra","Statistics","Optimization","Fuzzy Sets"]
    )

    if st.button("Generate Questions"):
        if st.session_state.groq_key:
            qs = generate_practice_questions(
                st.session_state.groq_key,
                prac_topic
            )
            st.session_state.practice_questions = qs
        else:
            st.error("Enter API Key")

    if "practice_questions" in st.session_state:
        for i, q in enumerate(st.session_state.practice_questions):
            if st.button(f"Q{i+1}"):
                st.session_state.user_text = q

    st.divider()

    if st.button("Clear History"):
        clear_all_history()

    if st.button("New Chat"):
        st.session_state.messages = []
        st.rerun()

# ── CHAT DISPLAY ──────────────────────────────
st.title("🧞 MathGenie AI")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("image"):
            st.image(msg["image"], width=250)

# ── KEYBOARD ───────────────────────────────────
with st.expander("⌨️ Math Keyboard"):

    for section, symbols in MATH_SYMBOLS.items():

        st.write(section)

        cols = st.columns(min(len(symbols), 10))

        for i, (col, sym) in enumerate(zip(cols, symbols)):
            with col:
                if st.button(sym, key=f"{section}_{i}"):
                    st.session_state.user_text += sym

# ── INPUT ──────────────────────────────────────
import streamlit as st

st.set_page_config(layout="wide")

# CSS
st.markdown("""
<style>
.block-container{
    padding-bottom: 80px;
}

.math-panel{
    position: fixed;
    bottom: 90px;
    right: 20px;
    background: white;
    padding: 10px;
    border-radius: 10px;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("MathGenie AI")

    if st.button("Generate Question"):
        st.write("Solve x² + 5x + 6 = 0")

# Main Chat
st.title("Math Solver")

st.write("Welcome to MathGenie AI")

# Floating keyboard
st.markdown("""
<div class="math-panel">
<b>Math Keyboard</b><br><br>

+  −  ×  ÷  √  π  ∫  x²

</div>
""", unsafe_allow_html=True)

# Chat input
question = st.chat_input("Type your math question")

if question:
    st.write("Question:", question)


# ── PROCESS ────────────────────────────────────
send_button=st.button("send")
if send button:
    st.write("Message Sent")

    if not st.session_state.groq_key:
        st.error("Enter API Key")
        st.stop()

    user_msg = {
        "role": "user",
        "content": question
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

                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[-8:]
                ]

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

            except Exception as e:
                st.error(f"Error: {e}")

    st.rerun()
