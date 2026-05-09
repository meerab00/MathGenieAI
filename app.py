
import streamlit as st
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage

# ─────────────────────────────
# PAGE CONFIG
# ─────────────────────────────
st.set_page_config(page_title="MathGenie AI", page_icon="🧞", layout="centered")

# ─────────────────────────────
# SESSION STATE
# ─────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# ─────────────────────────────
# TITLE
# ─────────────────────────────
st.title("🧞 MathGenie AI")
st.caption("Step-by-step Math Solver (LangChain + Groq)")

# ─────────────────────────────
# API KEY INPUT
# ─────────────────────────────
api_key = st.text_input("Enter GROQ_API_KEY", type="password")

if api_key:
    st.session_state.api_key = api_key

# ─────────────────────────────
# SYSTEM PROMPT (IMPORTANT)
# ─────────────────────────────
SYSTEM_PROMPT = """
You are an expert math tutor.

RULES:
- Solve step-by-step
- Use proper LaTeX for math (VERY IMPORTANT)
- Always format equations like:
  \frac{a}{b}, x^2, \int, \sqrt{}
- No plain text math like 5x/5
- Give short clear steps
- Final answer must be clearly highlighted
"""

# ─────────────────────────────
# DISPLAY CHAT HISTORY
# ─────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─────────────────────────────
# INPUT BOX
# ─────────────────────────────
question = st.text_input("Enter your math question (e.g. integrate x^2 + 5x)")

# ─────────────────────────────
# SUBMIT BUTTON
# ─────────────────────────────
if st.button("Solve 🚀"):

    if not st.session_state.api_key:
        st.error("Please enter GROQ API key")
        st.stop()

    if not question:
        st.warning("Please enter a question")
        st.stop()

    # user message save
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("assistant"):
        with st.spinner("Solving..."):

            try:
                # ─── LangChain + Groq Model ───
                llm = ChatGroq(
                    api_key=st.session_state.api_key,
                    model="llama3-70b-8192"
                )

                messages = [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(content=question)
                ]

                response = llm.invoke(messages)

                answer = response.content

                # ─── SHOW OUTPUT IN MATH FORMAT ───
                st.markdown("### Solution")
                st.markdown(f"$$ {answer} $$")

                # save assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:
                st.error(f"Error: {str(e)}")
