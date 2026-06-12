"""
utils/i18n.py

Internationalization utility to load locale JSON files and translate keys with formatting support.
"""

import os
import json

# Global translations dictionary
LOCALES = {}

def load_all_locales():
    """
    Loads translation dictionary files (en.json, hi.json, te.json) into memory.
    Resolves the directory path dynamically.
    """
    global LOCALES
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    locales_dir = os.path.join(base_dir, "locales")
    
    for lang in ["en", "hi", "te"]:
        filepath = os.path.join(locales_dir, f"{lang}.json")
        try:
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    LOCALES[lang] = json.load(f)
            else:
                LOCALES[lang] = {}
        except Exception:
            LOCALES[lang] = {}

def t(key: str, lang: str, **kwargs) -> str:
    """
    Translates a key into the specified language, falling back to English or the key name on failure.
    Formats the string using passed keyword arguments.

    Parameters:
        key (str): The translation dictionary key.
        lang (str): The language code ("en", "hi", "te").
        **kwargs: Variables to format in the translation string.

    Returns:
        str: The translated and formatted string.
    """
    # 1. Look up in requested language
    lang_dict = LOCALES.get(lang, {})
    val = lang_dict.get(key)
    
    # 2. Fall back to English
    if val is None:
        val = LOCALES.get("en", {}).get(key)
        
    # 3. Fall back to the key name itself
    if val is None:
        val = key
        
    # 4. Format variables if kwargs are provided
    if kwargs:
        try:
            return val.format(**kwargs)
        except Exception:
            return val
            
    return val

# Load locales once at module import
load_all_locales()
