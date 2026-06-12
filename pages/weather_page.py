"""
pages/weather_page.py

Streamlit page component for the Weather Advisor feature of Annadata AI.
Fetches weekly weather forecasts and provides AI actions for target crops.
"""

import streamlit as st
import config
from utils.i18n import t
from utils.l10n import fmt_number
from modules import weather

def render(lang: str, settings: dict):
    """
    Renders the weather dashboard and weather advice user interface.

    Parameters:
        lang (str): Language code ("en", "hi", "te").
        settings (dict): LLM settings configuration.
    """
    st.subheader(t("nav_weather", lang))

    # 3-column input form
    col1, col2, col3 = st.columns(3)
    
    with col1:
        district_input = st.text_input(
            t("select_district", lang),
            placeholder="e.g. Warangal",
            key="weather_district"
        )
        
    with col2:
        crop_selection = st.selectbox(
            t("select_crop", lang),
            options=config.COMMON_CROPS,
            key="weather_crop"
        )
        crop_clean = crop_selection.split("/")[0].strip()
        
    with col3:
        api_key_label = "OpenWeatherMap API Key (Optional) / ओपनवेदरमैप API की (वैकल्पिक) / ఓపెన్వెదర్‌మ్యాప్ API కీ (ఐచ్ఛికం)"
        weather_api_key = st.text_input(
            api_key_label,
            type="password",
            placeholder="Enter OpenWeatherMap API key",
            key="weather_api_key_input"
        )

    # Submission button
    fetch_btn = st.button(t("weather_fetch_btn", lang), type="primary")

    if fetch_btn:
        if not district_input.strip():
            st.warning("Please enter a district name.")
            return

        with st.spinner(t("loading_msg", lang)):
            try:
                # 1. Fetch weather forecast from backend module
                weather_data = weather.get_weather(
                    district=district_input.strip(),
                    weather_api_key=weather_api_key.strip()
                )
                
                if "error" in weather_data:
                    st.error(t("error_msg", lang, error=weather_data["error"]))
                    return
                
                # Render 7-day forecast grid
                st.write("---")
                st.subheader(f"📊 {t('weather_header', lang)} - {weather_data.get('location')}")
                
                forecast_list = weather_data.get("forecast", [])
                
                cols = st.columns(7)
                for i, day in enumerate(forecast_list):
                    if i >= 7:
                        break
                    with cols[i]:
                        # Format temperatures using locale-aware formatter
                        max_temp_fmt = fmt_number(day["temp_max"], lang)
                        min_temp_fmt = fmt_number(day["temp_min"], lang)
                        
                        st.metric(
                            label=day["date"],
                            value=f"{max_temp_fmt}°C / {min_temp_fmt}°C",
                            help=(
                                f"Humidity: {day['humidity']}%\n"
                                f"Wind: {day['wind_speed']} km/h\n"
                                f"Rain: {day['rain_mm']} mm"
                            )
                        )
                        # Render description
                        st.caption(f"☁️ {day['description'].title()}")
                
                # 2. Get AI Weather Advice
                st.write("---")
                advice_header_label = {
                    "en": f"💡 AI Farming Actions for {crop_clean} this week",
                    "hi": f"💡 इस सप्ताह {crop_selection.split('/')[1].strip()} की फसल के लिए AI सुझाव",
                    "te": f"💡 ఈ వారం {crop_selection.split('/')[2].strip()} పంట కొరకు AI సలహా"
                }
                st.subheader(advice_header_label.get(lang, advice_header_label["en"]))
                
                advice = weather.get_weather_advice(
                    crop=crop_clean,
                    forecast=weather_data,
                    lang=lang,
                    settings=settings
                )
                
                if advice.startswith("Error:"):
                    st.error(t("error_msg", lang, error=advice))
                else:
                    st.info(advice)
                    
            except Exception as e:
                st.error(t("error_msg", lang, error=str(e)))
