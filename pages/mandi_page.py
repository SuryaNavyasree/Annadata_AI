"""
pages/mandi_page.py

Streamlit page component for the Mandi Prices feature of Annadata AI.
Queries commodity pricing records and displays structured market analysis and advice.
"""

import streamlit as st
import config
from utils.i18n import t
from utils.l10n import fmt_price
from modules import mandi_prices

def render(lang: str, settings: dict):
    """
    Renders the Mandi pricing explorer and price analysis UI.

    Parameters:
        lang (str): Language code ("en", "hi", "te").
        settings (dict): LLM settings configuration.
    """
    st.subheader(t("nav_mandi", lang))

    # 3-column input configuration
    col1, col2, col3 = st.columns(3)
    
    with col1:
        commodity_selection = st.selectbox(
            t("mandi_commodity", lang),
            options=config.COMMON_CROPS,
            key="mandi_crop"
        )
        # Clean crop name for API call
        commodity_clean = commodity_selection.split("/")[0].strip()
        
    with col2:
        state_selection = st.selectbox(
            t("mandi_state", lang),
            options=config.INDIAN_STATES,
            key="mandi_state_select"
        )
        
    with col3:
        api_key_label = "data.gov.in API Key (Optional) / data.gov.in API की (वैकल्पिक) / data.gov.in API కీ (ఐచ్ఛికం)"
        mandi_api_key = st.text_input(
            api_key_label,
            type="password",
            placeholder="Enter API key",
            key="mandi_api_key_input"
        )

    # Submission button
    fetch_btn = st.button(t("mandi_fetch_btn", lang), type="primary")

    if fetch_btn:
        with st.spinner(t("loading_msg", lang)):
            try:
                # 1. Fetch Mandi records from backend module
                prices_list = mandi_prices.get_mandi_prices(
                    commodity=commodity_clean,
                    state=state_selection,
                    mandi_api_key=mandi_api_key.strip()
                )
                
                # Check for module errors
                if prices_list and "error" in prices_list[0]:
                    st.error(t("error_msg", lang, error=prices_list[0]["error"]))
                    return
                
                if not prices_list:
                    st.warning("No mandi price data found for selected criteria.")
                    return
                
                st.write("---")
                
                # Column Header Translations
                headers = {
                    "en": ["State", "District", "Market", "Commodity", "Min Price", "Max Price", "Modal Price", "Date"],
                    "hi": ["राज्य", "जिला", "बाजार", "वस्तु", "न्यूनतम मूल्य", "अधिकतम मूल्य", "औसत मूल्य", "तारीख"],
                    "te": ["రాష్ట్రం", "జిల్లా", "మార్కెట్", "ఉత్పత్తి", "కనీస ధర", "గరిష్ట ధర", "సగటు ధర", "తేదీ"]
                }
                h = headers.get(lang, headers["en"])
                
                # 2. Format prices with localization-aware currency helper
                formatted_records = []
                for p in prices_list:
                    formatted_records.append({
                        h[0]: p.get("state"),
                        h[1]: p.get("district"),
                        h[2]: p.get("market"),
                        h[3]: p.get("commodity"),
                        h[4]: fmt_price(p.get("min_price"), lang),
                        h[5]: fmt_price(p.get("max_price"), lang),
                        h[6]: fmt_price(p.get("modal_price"), lang),
                        h[7]: p.get("date")
                    })
                
                st.subheader(f"📈 Mandi Prices: {commodity_clean} ({state_selection})")
                st.dataframe(formatted_records, use_container_width=True)
                
                # 3. Fetch and display AI price advice
                st.write("---")
                advice_header_label = {
                    "en": "💡 AI Market Advisory",
                    "hi": "💡 AI मंडी व्यापार सलाह",
                    "te": "💡 AI మార్కెట్ సలహా"
                }
                st.subheader(advice_header_label.get(lang, advice_header_label["en"]))
                
                advice = mandi_prices.get_price_advice(
                    commodity=commodity_clean,
                    prices=prices_list,
                    lang=lang,
                    settings=settings
                )
                
                if advice.startswith("Error:"):
                    st.error(t("error_msg", lang, error=advice))
                else:
                    st.info(advice)
                    
            except Exception as e:
                st.error(t("error_msg", lang, error=str(e)))
