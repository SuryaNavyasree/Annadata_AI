"""
app.py
Main Streamlit entrypoint for the Annadata AI multilingual farmer assistant app.
"""

import sys
import os
import streamlit as st

st.set_page_config(
    page_title="Annadata AI",
    layout="wide",
    page_icon="🌾"
)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from utils.i18n import t

# Initialize session state
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

if "llm_settings" not in st.session_state:
    st.session_state["llm_settings"] = {
        "provider": "ollama",
        "model": "llama3",
        "api_key": ""
    }

lang = st.session_state["lang"]

# SIDEBAR
lang_display_to_code = {"English": "en", "हिंदी": "hi", "తెలుగు": "te"}

selected_lang_name = st.sidebar.selectbox(
    t("sidebar_language", lang),
    options=["English", "हिंदी", "తెలుగు"],
    index=["en", "hi", "te"].index(lang)
)

new_lang = lang_display_to_code[selected_lang_name]
if new_lang != st.session_state["lang"]:
    st.session_state["lang"] = new_lang
    st.rerun()

st.sidebar.divider()

local_label = t("sidebar_local_ollama", lang)
cloud_label = t("sidebar_cloud_byok", lang)
current_provider = st.session_state["llm_settings"]["provider"]

selected_provider = st.sidebar.radio(
    t("sidebar_ai_provider", lang),
    options=[local_label, cloud_label],
    index=0 if current_provider == "ollama" else 1
)

provider_code = "ollama" if selected_provider == local_label else "cloud"

api_key_val = ""

if provider_code == "ollama":
    model_options = [m for m in config.OLLAMA_MODELS if m != "llava"]
    current_model = st.session_state["llm_settings"]["model"]
    model_index = model_options.index(current_model) if current_model in model_options else 0
    selected_model = st.sidebar.selectbox(t("sidebar_select_model", lang), options=model_options, index=model_index)
else:
    model_options = config.CLOUD_MODELS
    current_model = st.session_state["llm_settings"]["model"]
    model_index = model_options.index(current_model) if current_model in model_options else 0
    selected_model = st.sidebar.selectbox(t("sidebar_select_model", lang), options=model_options, index=model_index)
    api_key_val = st.sidebar.text_input(
        t("sidebar_api_key", lang),
        value=st.session_state["llm_settings"].get("api_key", ""),
        type="password",
        placeholder=t("sidebar_api_key_placeholder", lang)
    )

st.session_state["llm_settings"] = {
    "provider": provider_code,
    "model": selected_model,
    "api_key": api_key_val
}

if provider_code == "cloud" and not api_key_val.strip():
    st.sidebar.warning(t("no_key_warning", lang))

# MAIN AREA
st.title(t("app_title", lang))
st.subheader(t("app_subtitle", lang))

tab_labels = [
    t("nav_crop", lang), t("nav_weather", lang), t("nav_mandi", lang),
    t("nav_pest", lang), t("nav_chat", lang), t("nav_schemes", lang)
]

tab_crop, tab_weather, tab_mandi, tab_pest, tab_chat, tab_schemes = st.tabs(tab_labels)

from pages import crop_advisor_page, weather_page, mandi_page, pest_page, chat_page, schemes_page

with tab_crop:
    crop_advisor_page.render(lang, st.session_state["llm_settings"])
with tab_weather:
    weather_page.render(lang, st.session_state["llm_settings"])
with tab_mandi:
    mandi_page.render(lang, st.session_state["llm_settings"])
with tab_pest:
    pest_page.render(lang, st.session_state["llm_settings"])
with tab_chat:
    chat_page.render(lang, st.session_state["llm_settings"])
with tab_schemes:
    schemes_page.render(lang, st.session_state["llm_settings"])
