"""
pages/schemes_page.py

Streamlit page component for the Government Schemes finder feature of Annadata AI.
Allows lookup of agricultural subsidies, crop insurance, and state schemes.
"""

import streamlit as st
import config
from utils.i18n import t
from modules import scheme_finder

# Localized labels for scheme properties
SCHEME_LABELS = {
    "en": {
        "benefit": "🎁 Benefit",
        "eligibility": "🧑‍🌾 Eligibility Criteria",
        "how_to_apply": "📝 How to Apply",
        "documents_needed": "📄 Documents Needed"
    },
    "hi": {
        "benefit": "🎁 योजना का लाभ",
        "eligibility": "🧑‍🌾 पात्रता मापदंड",
        "how_to_apply": "📝 आवेदन कैसे करें",
        "documents_needed": "📄 आवश्यक दस्तावेज"
    },
    "te": {
        "benefit": "🎁 పథకం ప్రయోజనం",
        "eligibility": "🧑‍🌾 అర్హత ప్రమాణాలు",
        "how_to_apply": "📝 దరఖాస్తు విధానం",
        "documents_needed": "📄 కావలసిన పత్రాలు"
    }
}

def render(lang: str, settings: dict):
    """
    Renders the government schemes finder user interface page.

    Parameters:
        lang (str): Language code ("en", "hi", "te").
        settings (dict): LLM settings configuration.
    """
    st.subheader(t("nav_schemes", lang))

    # 3-column input configuration layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        state_selection = st.selectbox(
            t("schemes_state", lang),
            options=config.INDIAN_STATES,
            key="schemes_state_select"
        )
        
    with col2:
        crop_selection = st.selectbox(
            t("schemes_crop", lang),
            options=config.COMMON_CROPS,
            key="schemes_crop_select"
        )
        crop_clean = crop_selection.split("/")[0].strip()
        
    with col3:
        land_size_input = st.number_input(
            t("schemes_land", lang),
            min_value=0.0,
            max_value=1000.0,
            value=2.5,
            step=0.5,
            key="schemes_land_input"
        )

    # Submission button
    find_btn = st.button(t("schemes_find_btn", lang), type="primary")

    if find_btn:
        with st.spinner(t("loading_msg", lang)):
            try:
                # 1. Fetch schemes from backend module
                schemes_list = scheme_finder.find_schemes(
                    state=state_selection,
                    crop=crop_clean,
                    land_size=float(land_size_input),
                    lang=lang,
                    settings=settings
                )
                
                # Check for execution errors
                if schemes_list and "error" in schemes_list[0]:
                    st.error(t("error_msg", lang, error=schemes_list[0]["error"]))
                    return
                
                if not schemes_list:
                    st.info("No matching schemes found for selected criteria.")
                    return
                
                st.write("---")
                l = SCHEME_LABELS.get(lang, SCHEME_LABELS["en"])
                
                # Render each scheme as a collapsible expander card
                for scheme in schemes_list:
                    scheme_title = f"🏛️ {scheme.get('scheme_name', 'N/A')}"
                    authority = scheme.get('authority', '')
                    
                    if authority:
                        scheme_title += f" ({authority})"
                        
                    with st.expander(scheme_title, expanded=True):
                        st.markdown(f"**{l['benefit']}**:\n{scheme.get('benefit', 'N/A')}")
                        st.markdown(f"**{l['eligibility']}**:\n{scheme.get('eligibility', 'N/A')}")
                        st.markdown(f"**{l['how_to_apply']}**:\n{scheme.get('how_to_apply', 'N/A')}")
                        st.markdown(f"**{l['documents_needed']}**:\n{scheme.get('documents_needed', 'N/A')}")
                        
            except Exception as e:
                st.error(t("error_msg", lang, error=str(e)))
