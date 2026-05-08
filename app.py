
if question or uploaded_file:

    if not st.session_state.groq_key:
        st.error("Please Enter Groq API Key")
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
                        question,
                        img_b64
                    )
                else:
                    response = get_groq_response(
                        st.session_state.groq_key,
                        system_prompt,
                        history_for_api
                    )

                if not response:
                    st.error("No response received")
                    st.stop()

                st.markdown(response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

                save_chat(display_q, st.session_state.messages)

            except Exception as e:
                st.error(f"Error: {e}")
