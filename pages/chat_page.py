"""
pages/chat_page.py

Streamlit page component for the Chat Assistant feature of Annadata AI.
Implements a multilingual conversation stream using standard chat widgets.
"""

import streamlit as st
from utils.i18n import t
from utils import llm_client

def render(lang: str, settings: dict):
    """
    Renders the interactive chat assistant interface.

    Parameters:
        lang (str): Language code ("en", "hi", "te").
        settings (dict): LLM settings configuration.
    """
    st.subheader(t("nav_chat", lang))

    # Initialize chat history if not already present
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Display clean chat reset option
    col_hdr, col_btn = st.columns([5, 1])
    with col_btn:
        if st.button(t("chat_clear", lang), key="clear_chat_history_btn", use_container_width=True):
            st.session_state["chat_history"] = []
            st.rerun()

    # Renders the message history log using st.chat_message
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Message input block at bottom of the page
    user_prompt = st.chat_input(t("chat_placeholder", lang))

    if user_prompt:
        # 1. Append user prompt and render it immediately
        st.session_state["chat_history"].append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(user_prompt)

        # 2. Query LLM and render response stream
        with st.chat_message("assistant"):
            with st.spinner(t("loading_msg", lang)):
                try:
                    system_prompt = (
                        f"{llm_client.get_language_instruction(lang)}\n"
                        "You are Annadata AI, an agricultural expert assistant. "
                        "Give helpful, precise, and actionable answers to farmers regarding crops, "
                        "weather, diseases, soils, and farming practices."
                    )
                    
                    response_text = llm_client.get_response(
                        prompt=user_prompt,
                        system_prompt=system_prompt,
                        settings=settings
                    )
                    
                    st.write(response_text)
                    
                    # 3. Append response to history
                    st.session_state["chat_history"].append({"role": "assistant", "content": response_text})
                    
                except Exception as e:
                    st.error(t("error_msg", lang, error=str(e)))
