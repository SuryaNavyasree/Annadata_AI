"""
pages/pest_page.py

Streamlit page component for the Pest & Disease Diagnosis feature of Annadata AI.
Accepts image uploads and crop details to return structured plant pathology analysis.
"""

import streamlit as st
from utils.i18n import t
from modules import pest_diagnosis

# Localized labels for diagnosis attributes
DIAGNOSIS_LABELS = {
    "en": {
        "disease_name": "🔍 Disease/Pest Name",
        "severity": "⚠️ Severity",
        "symptoms": "📋 Symptoms",
        "treatment": "💊 Treatment & Control Measures",
        "prevention": "🛡️ Preventative Measures",
        "urgency": "🚨 Urgency Level"
    },
    "hi": {
        "disease_name": "🔍 रोग/कीट का नाम",
        "severity": "⚠️ तीव्रता",
        "symptoms": "📋 लक्षण",
        "treatment": "💊 उपचार और नियंत्रण उपाय",
        "prevention": "🛡️ निवारक उपाय",
        "urgency": "🚨 तात्कालिकता स्तर"
    },
    "te": {
        "disease_name": "🔍 వ్యాధి/తెగులు పేరు",
        "severity": "⚠️ తీవ్రత",
        "symptoms": "📋 లక్షణాలు",
        "treatment": "💊 చికిత్స & నివారణ చర్యలు",
        "prevention": "🛡️ నివారణ మార్గాలు",
        "urgency": "🚨 అత్యవసర స్థాయి"
    }
}

def get_localized_severity(val: str, lang: str) -> tuple[str, str]:
    """
    Returns (display_text, color) for severity.
    """
    val = str(val).strip().upper()
    mapping = {
        "MILD": "MILD", "MODERATE": "MODERATE", "SEVERE": "SEVERE",
        "हल्का": "MILD", "मध्यम": "MODERATE", "गंभीर": "SEVERE",
        "తేలికపాటి": "MILD", "మితమైన": "MODERATE", "తీవ్రమైన": "SEVERE"
    }
    std_key = mapping.get(val, "MODERATE")
    display = {
        "en": {"MILD": "Mild", "MODERATE": "Moderate", "SEVERE": "Severe"},
        "hi": {"MILD": "हल्का", "MODERATE": "मध्यम", "SEVERE": "गंभीर"},
        "te": {"MILD": "తేలికపాటి", "MODERATE": "మితమైన", "SEVERE": "తీవ్రమైన"}
    }
    colors = {"MILD": "green", "MODERATE": "orange", "SEVERE": "red"}
    lang_display = display.get(lang, display["en"])
    return lang_display.get(std_key, val), colors.get(std_key, "orange")

def get_localized_urgency(val: str, lang: str) -> tuple[str, str]:
    """
    Returns (display_text, color) for urgency.
    """
    val = str(val).strip().upper()
    mapping = {
        "MONITOR": "MONITOR", "THIS WEEK": "THIS WEEK", "IMMEDIATE": "IMMEDIATE",
        "निगरानी": "MONITOR", "इस सप्ताह": "THIS WEEK", "तुरंत": "IMMEDIATE",
        "పర్యవేక్షించండి": "MONITOR", "ఈ వారం": "THIS WEEK", "తక్షణమే": "IMMEDIATE"
    }
    std_key = mapping.get(val, "THIS WEEK")
    display = {
        "en": {"MONITOR": "Monitor", "THIS WEEK": "This Week", "IMMEDIATE": "Immediate"},
        "hi": {"MONITOR": "निगरानी", "THIS WEEK": "इस सप्ताह", "IMMEDIATE": "तुरंत"},
        "te": {"MONITOR": "పర్యవేక్షించండి", "THIS WEEK": "ఈ వారం", "IMMEDIATE": "తక్షణమే"}
    }
    colors = {"MONITOR": "blue", "THIS WEEK": "orange", "IMMEDIATE": "red"}
    lang_display = display.get(lang, display["en"])
    return lang_display.get(std_key, val), colors.get(std_key, "orange")

def render(lang: str, settings: dict):
    """
    Renders the Pest & Disease Diagnosis user interface page.

    Parameters:
        lang (str): Language code ("en", "hi", "te").
        settings (dict): LLM settings configuration.
    """
    st.subheader(t("nav_pest", lang))

    # Two column layout: Left for inputs, Right for image preview
    col1, col2 = st.columns([3, 2])

    with col1:
        crop_input = st.text_input(
            t("pest_crop_label", lang),
            placeholder="e.g. Rice / Paddy"
        )

        uploaded_file = st.file_uploader(
            t("pest_upload", lang),
            type=["jpg", "jpeg", "png"]
        )

    with col2:
        if uploaded_file is not None:
            # Display uploaded image preview
            st.image(uploaded_file, caption="Uploaded Image Preview", use_container_width=True)

    # Submission button
    diagnose_btn = st.button(t("pest_diagnose_btn", lang), type="primary")

    if diagnose_btn:
        if not crop_input.strip():
            st.warning("Please enter a crop name.")
            return

        if uploaded_file is None:
            st.warning("Please upload a leaf/crop image first.")
            return

        with st.spinner(t("loading_msg", lang)):
            try:
                # Read image bytes
                image_bytes = uploaded_file.getvalue()
                
                # Call diagnosis backend module
                result = pest_diagnosis.diagnose_pest(
                    image_bytes=image_bytes,
                    crop=crop_input.strip(),
                    lang=lang,
                    settings=settings
                )
                
                # Check for module execution errors
                if "error" in result:
                    st.error(t("error_msg", lang, error=result["error"]))
                    return
                
                # Render results in structured cards
                st.write("---")
                l = DIAGNOSIS_LABELS.get(lang, DIAGNOSIS_LABELS["en"])
                
                severity_val = result.get("severity", "N/A")
                severity_display, sev_color = get_localized_severity(severity_val, lang)
                
                urgency_val = result.get("urgency", "N/A")
                urgency_display, urg_color = get_localized_urgency(urgency_val, lang)
                
                # Layout results
                st.markdown(f"### {l['disease_name']}: **{result.get('disease_name', 'N/A')}**")
                
                c_info1, c_info2 = st.columns(2)
                with c_info1:
                    st.markdown(f"{l['severity']}: :{sev_color}[**{severity_display}**]")
                with c_info2:
                    st.markdown(f"{l['urgency']}: :{urg_color}[**{urgency_display}**]")
                    
                st.markdown(f"**{l['symptoms']}**:\n{result.get('symptoms', 'N/A')}")
                st.markdown(f"**{l['treatment']}**:\n{result.get('treatment', 'N/A')}")
                st.markdown(f"**{l['prevention']}**:\n{result.get('prevention', 'N/A')}")

            except Exception as e:
                st.error(t("error_msg", lang, error=str(e)))
