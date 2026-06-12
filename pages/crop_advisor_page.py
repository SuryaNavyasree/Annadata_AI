"""
pages/crop_advisor_page.py

Streamlit page component for the Crop Advisor feature of Annadata AI.
Allows input of crop details and yields localized, structured seasonal farming advice.
"""

import streamlit as st
import datetime
import config
from utils.i18n import t
from modules import crop_advisor

# Localized labels mapping for crop advisor JSON fields
FIELD_LABELS = {
    "en": {
        "seasonal_plan": "📅 Seasonal Farming Plan",
        "fertilizer_schedule": "🧪 Fertilizer & Nutrient Schedule",
        "pest_watch": "🐛 Pest & Disease Watch",
        "harvest_window": "🌾 Expected Harvest Window",
        "tips": "💡 General Best Practices & Tips"
    },
    "hi": {
        "seasonal_plan": "📅 मौसमी फसल योजना",
        "fertilizer_schedule": "🧪 उर्वरक और पोषक तत्व अनुसूची",
        "pest_watch": "🐛 कीट और रोग निगरानी",
        "harvest_window": "🌾 कटाई का समय",
        "tips": "💡 सामान्य सुझाव और युक्तियां"
    },
    "te": {
        "seasonal_plan": "📅 కాలానుగుణ పంట ప్రణాళిక",
        "fertilizer_schedule": "🧪 ఎరువులు మరియు పోషకాల షెడ్యూల్",
        "pest_watch": "🐛 తెగుళ్లు మరియు వ్యాధుల నివారణ",
        "harvest_window": "🌾 పంట కోత సమయం",
        "tips": "💡 సాధారణ సూచనలు మరియు చిట్కాలు"
    }
}

def render(lang: str, settings: dict):
    """
    Renders the crop advisor user interface page.

    Parameters:
        lang (str): Language code ("en", "hi", "te").
        settings (dict): LLM settings configuration.
    """
    st.subheader(t("nav_crop", lang))
    
    # 2-column input form layout
    col1, col2 = st.columns(2)
    
    with col1:
        crop_selection = st.selectbox(
            t("select_crop", lang),
            options=config.COMMON_CROPS
        )
        
        # Clean crop selection (remove translated suffixes for backend logic)
        # e.g., "Wheat / गेहूं / గోధుమ" -> "Wheat"
        crop_clean = crop_selection.split("/")[0].strip()
        
        state_selection = st.selectbox(
            t("select_state", lang),
            options=config.INDIAN_STATES
        )
        
    with col2:
        district_input = st.text_input(
            t("select_district", lang),
            placeholder="e.g. Warangal"
        )
        
        sowing_date_input = st.date_input(
            t("sowing_date", lang),
            value=datetime.date.today()
        )

    # Submission button
    submit_btn = st.button(t("get_advice", lang), type="primary")

    if submit_btn:
        if not district_input.strip():
            st.warning("Please enter a district name.")
            return

        # Fetch advice under loading spinner
        with st.spinner(t("loading_msg", lang)):
            try:
                result = crop_advisor.get_crop_advice(
                    crop=crop_clean,
                    district=district_input.strip(),
                    state=state_selection,
                    sowing_date=str(sowing_date_input),
                    lang=lang,
                    settings=settings
                )
                
                if "error" in result:
                    st.error(t("error_msg", lang, error=result["error"]))
                    return
                
                # Display output as cards inside expanders
                st.write("---")
                labels = FIELD_LABELS.get(lang, FIELD_LABELS["en"])
                
                for key in ["seasonal_plan", "fertilizer_schedule", "pest_watch", "harvest_window", "tips"]:
                    val = result.get(key, "")
                    if val:
                        with st.expander(labels.get(key, key.replace("_", " ").title()), expanded=True):
                            st.write(val)
                            
            except Exception as e:
                st.error(t("error_msg", lang, error=str(e)))
