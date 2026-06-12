"""
utils/llm_client.py

Unified LLM client module using litellm to support text and vision tasks for both
local (Ollama) and cloud providers.
"""

import litellm
from config import OLLAMA_BASE_URL

litellm.telemetry = False

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

def get_language_instruction(lang: str) -> str:
    if lang == "hi":
        return "Respond in Hindi (हिंदी). Use Devanagari script."
    elif lang == "te":
        return "Respond in Telugu (తెలుగు). Use Telugu script."
    else:
        return "Respond in English."

def _is_openrouter_key(api_key: str) -> bool:
    return api_key.startswith("sk-or-")

def get_response(prompt: str, system_prompt: str, settings: dict) -> str:
    try:
        provider = settings.get("provider", "ollama")
        model_name = settings.get("model", "")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        if provider == "ollama":
            response = litellm.completion(
                model=f"ollama/{model_name}",
                messages=messages,
                api_base=OLLAMA_BASE_URL
            )
        elif provider == "cloud":
            api_key = settings.get("api_key", "")
            if _is_openrouter_key(api_key):
                response = litellm.completion(
                    model=f"openrouter/{model_name}",
                    messages=messages,
                    api_key=api_key,
                    api_base=OPENROUTER_BASE_URL
                )
            else:
                response = litellm.completion(
                    model=model_name,
                    messages=messages,
                    api_key=api_key
                )
        else:
            return f"Error: Unknown provider '{provider}'"

        if response and response.choices:
            return response.choices[0].message.content
        return "Error: Empty response received from the model."
    except Exception as e:
        return f"Error: {str(e)}"

def get_vision_response(prompt: str, image_base64: str, mime_type: str, settings: dict, system_prompt: str = "") -> str:
    try:
        provider = settings.get("provider", "ollama")
        model_name = settings.get("model", "")
        image_url = f"data:{mime_type};base64,{image_base64}"
        user_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_content})

        if provider == "ollama":
            response = litellm.completion(
                model="ollama/llava",
                messages=messages,
                api_base=OLLAMA_BASE_URL
            )
        elif provider == "cloud":
            api_key = settings.get("api_key", "")
            if _is_openrouter_key(api_key):
                response = litellm.completion(
                    model=f"openrouter/{model_name}",
                    messages=messages,
                    api_key=api_key,
                    api_base=OPENROUTER_BASE_URL
                )
            else:
                response = litellm.completion(
                    model=model_name,
                    messages=messages,
                    api_key=api_key
                )
        else:
            return f"Error: Unknown provider '{provider}'"

        if response and response.choices:
            return response.choices[0].message.content
        return "Error: Empty response received from the model."
    except Exception as e:
        return f"Error: {str(e)}"
