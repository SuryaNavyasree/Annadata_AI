"""
modules/scheme_finder.py

Module to identify relevant central and state government schemes for farmers based on their location,
crop, and land holding size.
"""

import json
from utils.llm_client import get_response, get_language_instruction
from modules.crop_advisor import clean_json_string

def find_schemes(
    state: str,
    crop: str,
    land_size: float,
    lang: str,
    settings: dict
) -> list[dict]:
    """
    Identifies relevant central and state-specific agricultural government schemes for a farmer.

    Parameters:
        state (str): The state name.
        crop (str): The name of the crop.
        land_size (float): The size of the land holding in acres.
        lang (str): Language code ("en", "hi", "te").
        settings (dict): LLM provider settings configuration.

    Returns:
        list[dict]: A list of dictionaries, each containing:
            - "scheme_name": Name of the government scheme.
            - "authority": "Central" or "State".
            - "benefit": Description of benefit.
            - "eligibility": Eligibility criteria.
            - "how_to_apply": Application process instructions.
            - "documents_needed": Required documents.
            If parsing fails, returns raw text wrapped in a fallback scheme dictionary.
            If an exception occurs, returns [{"error": str(e)}].
    """
    try:
        system_instruction = get_language_instruction(lang)
        system_prompt = (
            f"{system_instruction}\n"
            "You are an expert government welfare schemes advisor for Indian agriculture. "
            "Respond ONLY in JSON format, no explanation, no markdown, no backticks. "
            "The response must be a JSON array of objects matching this exact structure:\n"
            "[\n"
            "  {\n"
            '    "scheme_name": "...",\n'
            '    "authority": "Central/State",\n'
            '    "benefit": "...",\n'
            '    "eligibility": "...",\n'
            '    "how_to_apply": "...",\n'
            '    "documents_needed": "..."\n'
            "  }\n"
            "]"
        )

        lang_name = "Telugu (తెలుగు)" if lang == "te" else "Hindi (हिंदी)" if lang == "hi" else "English"
        user_prompt = (
            f"Identify all relevant central and state government agricultural schemes for a farmer with the following details:\n"
            f"- State: {state}\n"
            f"- Crop: {crop}\n"
            f"- Land Size: {land_size} acres\n\n"
            "For context, consider both central schemes and state-specific schemes, such as:\n"
            "- PM-KISAN (₹6000/year direct benefit)\n"
            "- PMFBY (Pradhan Mantri Fasal Bima Yojana - crop insurance)\n"
            "- PM Kisan Samman Nidhi\n"
            "- Kisan Credit Card (KCC)\n"
            "- Soil Health Card Scheme\n"
            "- Paramparagat Krishi Vikas Yojana (organic farming)\n"
            "- National Food Security Mission\n"
            f"- State-specific agricultural schemes for the state of {state}.\n\n"
            "Ensure the benefits, eligibility rules, and documents needed match the context of a farmer growing "
            f"{crop} on {land_size} acres in {state}. "
            f"You MUST translate all fields (scheme_name, authority, benefit, eligibility, how_to_apply, documents_needed) in the JSON response into {lang_name} using its native script."
        )

        raw_response = get_response(user_prompt, system_prompt, settings)

        if raw_response.startswith("Error:"):
            return [{"error": raw_response}]

        cleaned_response = clean_json_string(raw_response)

        try:
            schemes_list = json.loads(cleaned_response)
            if not isinstance(schemes_list, list):
                # If parsed json is not a list, raise error to go to fallback
                raise ValueError("Parsed JSON is not a list")
                
            # Validate list elements
            required_keys = ["scheme_name", "authority", "benefit", "eligibility", "how_to_apply", "documents_needed"]
            for scheme in schemes_list:
                for key in required_keys:
                    if key not in scheme:
                        scheme[key] = ""
            return schemes_list
            
        except Exception:
            # If parsing fails return [{"scheme_name": raw_text, "benefit": "", "eligibility": "", "how_to_apply": "", "documents_needed": ""}]
            return [{
                "scheme_name": raw_response,
                "authority": "",
                "benefit": "",
                "eligibility": "",
                "how_to_apply": "",
                "documents_needed": ""
            }]

    except Exception as e:
        return [{"error": str(e)}]
