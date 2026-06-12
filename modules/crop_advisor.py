"""
modules/crop_advisor.py

Module to provide detailed crop advice and quick home-screen tips in multiple languages.
"""

import json
import re
from utils.llm_client import get_response, get_language_instruction

def clean_json_string(text: str) -> str:
    """
    Cleans markdown backticks and wraps from JSON strings returned by LLMs.
    Extracts the first valid JSON object or array if extra data is present.
    """
    text = text.strip()
    # Remove markdown code block fences if present
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\n?```$", "", text)
    text = text.strip()
    
    # Try to find the start of a JSON object or array
    brace_idx = text.find('{')
    bracket_idx = text.find('[')
    
    if brace_idx == -1 and bracket_idx == -1:
        return text
        
    start_idx = brace_idx
    if bracket_idx != -1 and (brace_idx == -1 or bracket_idx < brace_idx):
        start_idx = bracket_idx
        
    decoder = json.JSONDecoder()
    try:
        obj, end_idx = decoder.raw_decode(text, idx=start_idx)
        return text[start_idx:end_idx]
    except Exception:
        # If raw_decode fails (for example, if the JSON is incomplete or invalid),
        # return the substring from start_idx onwards, or the original text, to let the parser raise a clean error.
        return text[start_idx:]

def get_crop_advice(
    crop: str,
    district: str,
    state: str,
    sowing_date: str,
    lang: str,
    settings: dict
) -> dict:
    """
    Generates a structured, language-localized seasonal farming plan for a given crop and location.

    Parameters:
        crop (str): The name of the crop.
        district (str): The district location.
        state (str): The state location.
        sowing_date (str): The sowing date of the crop.
        lang (str): Language code ("en", "hi", "te").
        settings (dict): LLM provider settings configuration.

    Returns:
        dict: A dictionary containing:
            - "seasonal_plan": Description of seasonal plan.
            - "fertilizer_schedule": Detailed fertilizer/nutrient recommendations.
            - "pest_watch": Common pests/diseases and control measures.
            - "harvest_window": Expected time window and tips for harvesting.
            - "tips": General best practices.
            Or {"error": "..."} in case of system failure.
    """
    try:
        system_instruction = get_language_instruction(lang)
        system_prompt = (
            f"{system_instruction}\n"
            "You are an expert agricultural scientist advising a farmer. "
            "Respond ONLY in JSON format, no explanation, no markdown, no backticks. "
            "The JSON structure must exactly match this template:\n"
            "{\n"
            '  "seasonal_plan": "...",\n'
            '  "fertilizer_schedule": "...",\n'
            '  "pest_watch": "...",\n'
            '  "harvest_window": "...",\n'
            '  "tips": "..."\n'
            "}"
        )

        lang_name = "Telugu (తెలుగు)" if lang == "te" else "Hindi (हिंदी)" if lang == "hi" else "English"
        user_prompt = (
            f"Provide a complete farming plan for the following details:\n"
            f"- Crop: {crop}\n"
            f"- District: {district}\n"
            f"- State: {state}\n"
            f"- Sowing Date: {sowing_date}\n\n"
            "Ensure the responses are comprehensive, practical, and highly relevant to Indian agriculture. "
            f"You MUST translate all plan details (seasonal_plan, fertilizer_schedule, pest_watch, harvest_window, tips) in the JSON response into {lang_name} using its native script."
        )

        raw_response = get_response(user_prompt, system_prompt, settings)

        if raw_response.startswith("Error:"):
            return {"error": raw_response}

        cleaned_response = clean_json_string(raw_response)

        try:
            advice_dict = json.loads(cleaned_response)
            # Ensure all keys exist in the returned dictionary
            required_keys = ["seasonal_plan", "fertilizer_schedule", "pest_watch", "harvest_window", "tips"]
            for key in required_keys:
                if key not in advice_dict:
                    advice_dict[key] = ""
            return advice_dict
        except (json.JSONDecodeError, TypeError):
            # If JSON parsing fails, return the raw text under key "seasonal_plan"
            # and empty strings for other keys as per instructions.
            return {
                "seasonal_plan": raw_response,
                "fertilizer_schedule": "",
                "pest_watch": "",
                "harvest_window": "",
                "tips": ""
            }

    except Exception as e:
        return {"error": str(e)}

def get_quick_tip(crop: str, lang: str, settings: dict) -> str:
    """
    Returns one short farming tip for the specified crop in the user's language.

    Parameters:
        crop (str): The name of the crop.
        lang (str): Language code ("en", "hi", "te").
        settings (dict): LLM provider settings configuration.

    Returns:
        str: A short, 1-2 sentence farming tip, or an error string starting with "Error:".
    """
    try:
        system_instruction = get_language_instruction(lang)
        system_prompt = (
            f"{system_instruction}\n"
            "You are a helpful farmer assistant. Provide a single, quick, actionable farming tip."
        )
        
        user_prompt = (
            f"Give me one short, helpful farming tip for {crop} crop. "
            "It must be specific, actionable, and at most 2 sentences."
        )
        
        response = get_response(user_prompt, system_prompt, settings)
        return response
    except Exception as e:
        return f"Error: {str(e)}"
