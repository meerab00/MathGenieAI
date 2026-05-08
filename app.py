import streamlit as st
from utils.groq_client import get_groq_response, get_groq_vision_response
from utils.pdf_export import export_chat_to_pdf
from utils.graph_plotter import plot_graph, should_plot_graph, extract_graph_expr
from utils.practice_gen import generate_practice_questions
from utils.history_manager import save_chat, load_chats, clear_all_history
from utils.formula_sheet import FORMULA_SHEET
from utils.system_prompt import build_system_prompt
from utils.math_keyboard import MATH_SYMBOLS
import base64

st.set_page_config(
    page_title="MathGenie AI",
    page_icon="🧞",
    layout="wide",
    initial_sidebar_state="expanded",
)

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "topic" not in st.session_state:
    st.session_state.topic = "General"
if "groq_key" not in st.session_state:
    try:
        st.session_state.groq_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        st.session_state.groq_key = ""

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧞 MathGenie AI")
    st.markdown("*AI-Powered Math Solver*")
    st.divider()

    st.markdown("### 🔑 Groq API Key")
    api_key = st.text_input(
        "Enter your free Groq key",
        type="password",
        value=st.session_state.groq_key,
        placeholder="gsk_...",
        help="Free key at: https://console.groq.com/keys",
    )
    if api_key:
        st.session_state.groq_key = api_key
        st.success("✅ Key saved!")

    st.divider()

    st.markdown("### 📚 Topic")
    topic = st.selectbox(
        "Select subject",
        ["General", "Calculus", "Algebra", "Statistics",
         "Optimization Theory", "Fuzzy Set Theory",
         "Linear Algebra", "ODE / PDE", "Number Theory"],
        index=["General","Calculus","Algebra","Statistics",
               "Optimization Theory","Fuzzy Set Theory",
               "Linear Algebra","ODE / PDE","Number Theory"].index(st.session_state.topic),
    )
    st.session_state.topic = topic

    st.divider()

    st.markdown("### 📐 Formula Sheet")
    for subject, formulas in FORMULA_SHEET.items():
        with st.expander(subject):
            for f in formulas:
                st.code(f, language=None)

    st.divider()

    st.markdown("### 📝 Practice Questions")
    prac_topic = st.selectbox(
        "Choose topic",
        ["Calculus", "Algebra", "Statistics", "Optimization", "Fuzzy Sets"],
        key="prac_topic",
    )
    if st.button("⚡ Generate Questions", use_container_width=True):
        if not st.session_state.groq_key:
            st.error("API key enter karein pehle!")
        else:
            with st.spinner("Generating..."):
                questions = generate_practice_questions(
                    st.session_state.groq_key, prac_topic
                )
            st.session_state.practice_questions = questions

    if "practice_questions" in st.session_state:
        for i, q in enumerate(st.session_state.practice_questions, 1):
            if st.button(f"Q{i}: {q[:50]}...", key=f"pq_{i}", use_container_width=True):
                st.session_state.prefill_question = q

    st.divider()

    st.markdown("### 💬 Chat History")
    history = load_chats()
    if history:
        for i, chat in enumerate(history[:8]):
            if st.button(f"📌 {chat['question'][:40]}...", key=f"hist_{i}", use_container_width=True):
                st.session_state.messages = chat["messages"]
                st.rerun()
    else:
        st.caption("No history yet")

    if st.button("🗑️ Clear History", use_container_width=True):
        clear_all_history()
        st.success("Cleared!")

    st.divider()

    st.markdown("### 📄 Export")
    if st.button("⬇️ Download Full Chat PDF", use_container_width=True):
        if st.session_state.messages:
            pdf_bytes = export_chat_to_pdf(st.session_state.messages)
            st.download_button(
                "📥 Save PDF", data=pdf_bytes,
                file_name="MathGenie_Solution.pdf",
                mime="application/pdf", use_container_width=True,
            )
        else:
            st.warning("No messages to export!")

    if st.button("🔄 New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── MAIN ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
    <h1>🧞 MathGenie AI</h1>
    <p>Calculus • Algebra • Statistics • Optimization • Fuzzy Sets</p>
</div>
""", unsafe_allow_html=True)

cols = st.columns(8)
topics_short = ["General","Calculus","Algebra","Statistics",
                "Optimization Theory","Fuzzy Set Theory","Linear Algebra","ODE / PDE"]
icons = ["🧮","∫","α","σ","⚡","〜","[]","∂"]
for i, (col, t, ic) in enumerate(zip(cols, topics_short, icons)):
    with col:
        if st.button(f"{ic} {t.split()[0]}", key=f"pill_{i}",
                     type="primary" if st.session_state.topic == t else "secondary",
                     use_container_width=True):
            st.session_state.topic = t
            st.rerun()

st.divider()

# ── CHAT DISPLAY ──────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
<div class="welcome-box">
    <h2>Welcome to MathGenie AI! ✨</h2>
    <p>Aapka personal math tutor. Koi bhi question likhein ya photo upload karein.</p>
    <div class="feature-row">
        <div class="feat">📸 Photo Upload</div>
        <div class="feat">📊 Graph Plot</div>
        <div class="feat">📄 PDF Export</div>
        <div class="feat">⌨️ Math Keyboard</div>
        <div class="feat">📝 Practice Qs</div>
        <div class="feat">💬 Chat History</div>
    </div>
</div>
""", unsafe_allow_html=True)

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"], avatar="🧞" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            col1, col2, _ = st.columns([1, 1, 5])
            with col1:
                if st.button("📋 Copy", key=f"copy_{i}"):
                    st.code(msg["content"])
            with col2:
                pdf_b = export_chat_to_pdf([msg])
                st.download_button("⬇ PDF", data=pdf_b,
                                   file_name=f"solution_{i}.pdf",
                                   mime="application/pdf", key=f"pdf_{i}")
            if "graph_expr" in msg:
                fig = plot_graph(msg["graph_expr"])
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
        if msg.get("image") is not None:
            st.image(msg["image"], width=280)

# ── MATH KEYBOARD ─────────────────────────────────────────────────────────────
with st.expander("⌨️ Math Keyboard — click a symbol to copy", expanded=False):
    for section, symbols in MATH_SYMBOLS.items():
        st.markdown(f"**{section}**")
        kb_cols = st.columns(min(len(symbols), 12))
        for j, (col, sym) in enumerate(zip(kb_cols, symbols)):
            with col:
                if st.button(sym, key=f"kb_{section}_{j}"):
                    st.session_state.kb_insert = sym
    if "kb_insert" in st.session_state:
        st.info(f"Copied: `{st.session_state.kb_insert}` — paste it in the input box below!")

# ── INPUT ─────────────────────────────────────────────────────────────────────
st.divider()
col_img, col_input = st.columns([1, 4])

with col_img:
    uploaded_file = st.file_uploader(
        "📷 Upload Image", type=["jpg","jpeg","png","webp"],
        label_visibility="collapsed",
    )
    if uploaded_file:
        st.image(uploaded_file, caption="Ready to solve", width=140)

with col_input:
    prefill = st.session_state.pop("prefill_question", "")
    user_input = st.chat_input(
        placeholder="Math question likhein... e.g. 'Integrate x²·sin(x)' ya 'Explain KKT conditions'",
    )

question = user_input or prefill

# ── PROCESS ───────────────────────────────────────────────────────────────────
if question or uploaded_file:
    if not st.session_state.groq_key:
        st.error("⚠️ Sidebar mein Groq API key enter karein! Free at: console.groq.com/keys")
        st.stop()

    display_q = question or "📷 Image uploaded — please solve this math problem."
    user_msg = {"role": "user", "content": display_q}

    img_bytes = None
    if uploaded_file:
        img_bytes = uploaded_file.read()
        user_msg["image"] = img_bytes

    st.session_state.messages.append(user_msg)

    with st.chat_message("assistant", avatar="🧞"):
        with st.spinner("🧞 MathGenie thinking..."):
            system_prompt = build_system_prompt(st.session_state.topic)
            history_for_api = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[-8:]
                if isinstance(m.get("content"), str)
            ]
            try:
                if img_bytes:
                    img_b64 = base64.b64encode(img_bytes).decode()
                    response = get_groq_vision_response(
                        st.session_state.groq_key, system_prompt,
                        question or "Solve this math problem step by step.", img_b64,
                    )
                else:
                    response = get_groq_response(
                        st.session_state.groq_key, system_prompt, history_for_api,
                    )

                graph_expr = extract_graph_expr(response)
                clean = response.replace(f"GRAPH_EXPR: {graph_expr}", "").strip() if graph_expr else response

                st.markdown(clean)

                if graph_expr:
                    fig = plot_graph(graph_expr)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)

                col1, col2, _ = st.columns([1, 1, 5])
                with col1:
                    if st.button("📋 Copy", key="copy_new"):
                        st.code(clean)
                with col2:
                    pdf_b = export_chat_to_pdf([{"role":"assistant","content":clean}])
                    st.download_button("⬇ PDF", data=pdf_b,
                                       file_name="solution.pdf",
                                       mime="application/pdf", key="pdf_new")

                ai_msg = {"role": "assistant", "content": clean}
                if graph_expr:
                    ai_msg["graph_expr"] = graph_expr
                st.session_state.messages.append(ai_msg)
                save_chat(display_q, st.session_state.messages)

            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.info("💡 API key check karein — free: console.groq.com/keys")

    st.rerun()
