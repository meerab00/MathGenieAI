
import streamlit as st
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq

# ─────────────────────────────
# PAGE CONFIG
# ─────────────────────────────
st.set_page_config(
    page_title="MathGenie AI",
    page_icon="🧞",
    layout="centered"
)

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
st.caption("LangChain + Groq Step-by-Step Math Solver")

# ─────────────────────────────
# API KEY INPUT
# ─────────────────────────────
api_key = st.text_input("Enter GROQ_API_KEY", type="password")

if api_key:
    st.session_state.api_key = api_key

# ─────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────
SYSTEM_PROMPT = """
You are an expert math tutor.

Rules:
- Solve step-by-step
- Use proper LaTeX for all math:
  \frac{}, x^2, \int, \sqrt{}
- NEVER use plain text math like 5x/5
- Keep steps short and clear
- Highlight final answer
"""

# ─────────────────────────────
# CHAT HISTORY
# ─────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─────────────────────────────
# INPUT
# ─────────────────────────────
question = st.text_input("Enter your math question (e.g. integrate x^2 + 5x)")

# ─────────────────────────────
# SUBMIT BUTTON
# ─────────────────────────────
if st.button("Solve 🚀"):

    if not st.session_state.api_key:
        st.error("Please enter API key")
        st.stop()

    if not question:
        st.warning("Enter a question")
        st.stop()

    # save user message
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("assistant"):
        with st.spinner("Solving..."):

            try:
                # ─── UPDATED GROQ MODEL ───
                llm = ChatGroq(
                    api_key=st.session_state.api_key,
                    model="llama-3.1-70b-versatile"
                )

                messages = [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(content=question)
                ]

                response = llm.invoke(messages)

                answer = response.content

                # ─── SHOW MATH OUTPUT ───
                st.markdown("### Solution")
                st.markdown(f"$$ {answer} $$")

                # save assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:
                st.error(f"Error: {str(e)}")
