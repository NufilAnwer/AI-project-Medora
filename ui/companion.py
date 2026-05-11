import streamlit as st
from services.companion_engine import get_companion_response

def show_companion_chat():
    st.title("🤗 Relieve Loneliness")
    st.caption("Talk to your AI companion. You're never alone here.")

    if "companion_history" not in st.session_state:
        st.session_state.companion_history = []

    for msg in st.session_state.companion_history:
        st.chat_message(msg["role"]).write(msg["content"])

    user_input = st.chat_input("Say something...")
    if user_input:
        st.chat_message("user").write(user_input)
        st.session_state.companion_history.append({"role": "user", "content": user_input})

        response = get_companion_response(user_input, st.session_state.companion_history)
        st.chat_message("assistant").write(response)
        st.session_state.companion_history.append({"role": "assistant", "content": response})

    if st.button("🚪 Back to Dashboard", key="companion_logout"):
        st.session_state.page = "dashboard"
        st.rerun()
