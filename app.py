
import streamlit as st

st.set_page_config(page_title="MathGenie Safe", page_icon="🧞")

# ── SESSION ──
if "text" not in st.session_state:
    st.session_state.text = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

# ── TITLE ──
st.title("🧞 MathGenie (Safe Mode)")

# ── CHAT DISPLAY ──
for m in st.session_state.messages:
    st.chat_message(m["role"]).markdown(m["content"])

# ── KEYBOARD (SAFE) ──
symbols = ["+", "-", "*", "/", "=", "x", "^2", "(", ")"]

st.write("⌨️ Keyboard")
cols = st.columns(5)

for i, s in enumerate(symbols):
    if cols[i % 5].button(s, key=f"k{i}"):
        st.session_state.text += s

# ── INPUT ──
user_input = st.text_input("Type question", value=st.session_state.text)

st.session_state.text = user_input

# ── SEND BUTTON ──
send = st.button("Solve")

# ── PROCESS (NO API = NO ERROR) ──
if send and user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # dummy answer (safe testing)
    answer = f"Step 1: Received question\nStep 2: {user_input}\nStep 3: (AI disabled safe mode)"

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    st.rerun()
