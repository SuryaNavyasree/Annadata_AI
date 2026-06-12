"""
config.py

Central configuration file containing constants, supported languages, list of common crops,
and state metadata, as well as API endpoints for the weather and Mandi services.
"""

SUPPORTED_LANGUAGES = ["en", "hi", "te"]

LANGUAGE_NAMES = {
  "en": "English",
  "hi": "हिंदी",
  "te": "తెలుగు"
}

LANGUAGE_FULL_NAMES = {
  "en": "English",
  "hi": "Hindi",
  "te": "Telugu"
}

OLLAMA_BASE_URL = "http://localhost:11434"

OLLAMA_MODELS = ["llama2", "mistral", "llama3", "gemma2", "llava"]

CLOUD_MODELS = [
  "gpt-4o",
  "claude-sonnet-4-6",
  "gemini-1.5-pro",
  "openrouter/free",
  "openrouter/meta-llama/llama-3.2-3b-instruct:free",
  "openrouter/meta-llama/llama-3.3-70b-instruct:free",
  "groq/llama-3.3-70b-versatile",
  "groq/llama-3.3-70b-specdec",
  "groq/llama-3.1-70b-versatile"
]

COMMON_CROPS = [
  "Wheat / गेहूं / గోధుమ",
  "Rice / धान / వరి",
  "Maize / मक्का / మొక్కజొన్న",
  "Cotton / कपास / పత్తి",
  "Sugarcane / गन्ना / చెరకు",
  "Groundnut / मूंगफلی / వేరుశెనగ",
  "Tomato / टमाटर / టమాటో",
  "Onion / प्याज / ఉల్లిపాయ",
  "Soybean / सोयाबीन / సోయాబీన్",
  "Chilli / मिर्च / మిర్చి"
]

INDIAN_STATES = [
  "Andhra Pradesh", "Telangana", "Maharashtra",
  "Uttar Pradesh", "Punjab", "Haryana",
  "Madhya Pradesh", "Rajasthan", "Karnataka",
  "Tamil Nadu", "Gujarat", "Bihar",
  "West Bengal", "Odisha", "Assam"
]

WEATHER_API_BASE = "https://api.openweathermap.org/data/2.5"
MANDI_API_BASE = "https://api.data.gov.in/resource"
MANDI_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
