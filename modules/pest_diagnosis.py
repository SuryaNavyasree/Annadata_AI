"""
modules/pest_diagnosis.py

Module to diagnose crop diseases, pests, or nutrient deficiencies using image input.
Provides a text-based LLM fallback for non-vision environments.
"""

import base64
import json
import io
from PIL import Image
from utils.llm_client import get_vision_response, get_response, get_language_instruction
from modules.crop_advisor import clean_json_string

def format_value_to_string(val) -> str:
    """
    Recursively converts dictionary or list values into clean, formatted markdown strings.
    """
    if isinstance(val, str):
        return val.strip()
    if isinstance(val, list):
        cleaned_items = []
        for item in val:
            formatted = format_value_to_string(item)
            if formatted:
                cleaned_items.append(formatted)
        return ", ".join(cleaned_items)
    if isinstance(val, dict):
        lines = []
        for k, v in val.items():
            formatted_v = format_value_to_string(v)
            if formatted_v:
                key_label = str(k).replace("_", " ").title()
                lines.append(f"- **{key_label}**: {formatted_v}")
        return "\n".join(lines)
    if val is None:
        return ""
    return str(val).strip()

def diagnose_pest(
    image_bytes: bytes,
    crop: str,
    lang: str,
    settings: dict
) -> dict:
    """
    Diagnoses crop health issues from image bytes using vision capabilities of the LLM.
    Falls back to a text-only prompt describing a common disease/pest for the crop if vision
    fails or is not supported.

    Parameters:
        image_bytes (bytes): The raw image bytes of the affected plant.
        crop (str): The name of the crop.
        lang (str): Language code ("en", "hi", "te").
        settings (dict): LLM provider settings configuration.

    Returns:
        dict: A dictionary containing:
            - "disease_name": Name of diagnosed disease/pest.
            - "severity": "mild", "moderate", or "severe".
            - "symptoms": Observed or likely symptoms.
            - "treatment": Chemical/organic control measures.
            - "prevention": Actionable preventative measures.
            - "urgency": "immediate", "this week", or "monitor".
            Or {"error": "..."} in case of system failure.
    """
    try:
        # 1. Base64 encode the image bytes
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        # 2. Detect mime_type using Pillow
        try:
            img = Image.open(io.BytesIO(image_bytes))
            mime_type = img.get_format_mimetype()
        except Exception:
            mime_type = "image/jpeg"

        system_instruction = get_language_instruction(lang)
        if lang == "te":
            lang_detail = (
                "All text values in the JSON (disease_name, symptoms, treatment, prevention) MUST be completely written/translated in Telugu (తెలుగు) using Telugu script. "
                "Translate severity (must be తేలికపాటి, మితమైన, or తీవ్రమైన) and urgency (must be తక్షణమే, ఈ వారం, or పర్యవేక్షించండి) as well."
            )
        elif lang == "hi":
            lang_detail = (
                "All text values in the JSON (disease_name, symptoms, treatment, prevention) MUST be completely written/translated in Hindi (हिंदी) using Devanagari script. "
                "Translate severity (must be हल्का, मध्यम, or गंभीर) and urgency (must be तुरंत, इस सप्ताह, or निगरानी) as well."
            )
        else:
            lang_detail = "Respond in English."

        system_prompt = (
            f"{system_instruction}\n"
            f"{lang_detail}\n"
            "You are an expert plant pathologist advisor. "
            "Respond ONLY in JSON format, no explanation, no markdown, no backticks. "
            "The JSON structure must exactly match this template:\n"
            "{\n"
            '  "disease_name": "...",\n'
            '  "severity": "mild/moderate/severe",\n'
            '  "symptoms": "...",\n'
            '  "treatment": "...",\n'
            '  "prevention": "...",\n'
            '  "urgency": "immediate/this week/monitor"\n'
            "}"
        )

        # 3. Build vision prompt
        lang_name = "Telugu (తెలుగు)" if lang == "te" else "Hindi (हिंदी)" if lang == "hi" else "English"
        vision_prompt = (
            f"This is a photo of a {crop} plant. "
            "Identify any disease, pest, or deficiency visible. "
            f"You MUST translate the disease_name, symptoms, treatment, prevention, severity, and urgency fields in the JSON response into {lang_name} using its native script."
        )

        # 4. Call get_vision_response
        raw_response = get_vision_response(
            prompt=vision_prompt,
            image_base64=image_base64,
            mime_type=mime_type,
            settings=settings,
            system_prompt=system_prompt
        )

        is_error_response = raw_response.startswith("Error:")
        
        # 5 & 6. Parse JSON from response. If parse fails or error occurs, fallback.
        if not is_error_response:
            cleaned_response = clean_json_string(raw_response)
            try:
                diagnosis_dict = json.loads(cleaned_response)
                # Validate the dictionary structure has the correct keys
                required_keys = ["disease_name", "severity", "symptoms", "treatment", "prevention", "urgency"]
                if all(k in diagnosis_dict for k in required_keys):
                    # Format all fields to clean string types
                    for k in required_keys:
                        diagnosis_dict[k] = format_value_to_string(diagnosis_dict[k])
                    return diagnosis_dict
            except Exception:
                pass # Proceed to fallback

        # Fallback block
        return _run_text_fallback(crop, lang, settings, system_prompt)

    except Exception as e:
        return {"error": str(e)}

def _run_text_fallback(crop: str, lang: str, settings: dict, system_prompt: str) -> dict:
    """
    Executes a text-only fallback request targeting a typical disease for the given crop.
    """
    # Map common diseases to crops to make mock diagnosis high quality
    crop_diseases = {
        "rice": "Blast disease (Magnaporthe oryzae)",
        "wheat": "Leaf Rust (Puccinia triticina)",
        "maize": "Fall Armyworm (Spodoptera frugiperda)",
        "cotton": "Pink Bollworm",
        "sugarcane": "Red Rot disease",
        "groundnut": "Tikka Leaf Spot (Cercospora)",
        "tomato": "Early Blight",
        "onion": "Purple Blotch",
        "soybean": "Rust",
        "chilli": "Leaf Curl Virus"
    }
    
    # Try to find matching disease
    crop_key = crop.lower()
    common_disease = "a common fungal or insect pest infestation"
    for k, v in crop_diseases.items():
        if k in crop_key:
            common_disease = v
            break

    lang_name = "Telugu (తెలుగు)" if lang == "te" else "Hindi (हिंदी)" if lang == "hi" else "English"
    fallback_prompt = (
        f"This is a text-only fallback request since the vision service is unavailable. "
        f"Generate a diagnosis report for a {crop} plant affected by {common_disease} in Indian agricultural conditions. "
        "Choose only one disease or pest to diagnose and return exactly one JSON object. "
        "Ensure all details are structured and practical. "
        f"You MUST translate the disease_name, symptoms, treatment, prevention, severity, and urgency fields in the JSON response into {lang_name} using its native script."
    )

    raw_response = get_response(fallback_prompt, system_prompt, settings)
    if raw_response.startswith("Error:"):
        return {"error": raw_response}

    cleaned_response = clean_json_string(raw_response)
    try:
        diagnosis_dict = json.loads(cleaned_response)
        required_keys = ["disease_name", "severity", "symptoms", "treatment", "prevention", "urgency"]
        for k in required_keys:
            if k not in diagnosis_dict:
                diagnosis_dict[k] = "N/A"
            else:
                diagnosis_dict[k] = format_value_to_string(diagnosis_dict[k])
        return diagnosis_dict
    except Exception as e:
        return {"error": f"JSON parsing failed for fallback response: {str(e)}. Raw text: {raw_response}"}
