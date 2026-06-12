"""
test_frontend.py

Unit tests for the Annadata AI frontend utilities.
Validates translation files lookup, localizations, and formatting helpers.
"""

import sys
import os
import importlib.util
import unittest
from datetime import date

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
mitra_dir = os.path.abspath(os.path.join(current_dir, "../Kisaan_Mitra"))

sys.path.append(current_dir)
sys.path.append(mitra_dir)

# Import frontend utils to bind namespace
import utils

# Register Kisaan_Mitra's utils.llm_client manually to avoid name conflict with frontend utils
llm_client_path = os.path.join(mitra_dir, "utils", "llm_client.py")
if os.path.exists(llm_client_path):
    spec = importlib.util.spec_from_file_location("utils.llm_client", llm_client_path)
    llm_client_module = importlib.util.module_from_spec(spec)
    sys.modules["utils.llm_client"] = llm_client_module
    spec.loader.exec_module(llm_client_module)
    # Add to the utils package namespace
    utils.llm_client = llm_client_module

from utils.i18n import t, LOCALES
from utils.l10n import fmt_price, fmt_date, fmt_number
from pages import crop_advisor_page, weather_page, mandi_page, pest_page, chat_page, schemes_page

class TestAnnadataFrontend(unittest.TestCase):

    def test_translation_locales_loaded(self):
        """Verify that all locale translation keys are populated in memory."""
        self.assertIn("en", LOCALES)
        self.assertIn("hi", LOCALES)
        self.assertIn("te", LOCALES)
        
        # Check specific key translations
        self.assertEqual(LOCALES["en"]["app_title"], "Annadata AI")
        self.assertEqual(LOCALES["hi"]["app_title"], "अन्नदाता AI")
        self.assertEqual(LOCALES["te"]["app_title"], "అన్నదాత AI")
        
        self.assertEqual(LOCALES["hi"]["nav_crop"], "फसल सलाह")
        self.assertEqual(LOCALES["te"]["nav_crop"], "పంట సలహా")

    def test_translation_lookups(self):
        """Verify the translation function behaves correctly with lookup fallbacks."""
        # Simple lookup
        self.assertEqual(t("app_title", "en"), "Annadata AI")
        self.assertEqual(t("app_title", "hi"), "अन्नदाता AI")
        self.assertEqual(t("app_title", "te"), "అన్నదాత AI")
        
        # Fallback to English if missing in local
        self.assertEqual(t("sidebar_select_model", "en"), "Select AI Model")
        
        # Fallback to key itself if missing completely
        self.assertEqual(t("nonexistent_key_xyz", "hi"), "nonexistent_key_xyz")

    def test_translation_formatting(self):
        """Verify string template parameters are injected dynamically by translation lookup."""
        self.assertEqual(
            t("error_msg", "en", error="Timeout Exception"),
            "An error occurred: Timeout Exception"
        )
        self.assertEqual(
            t("error_msg", "hi", error="समय सीमा समाप्त"),
            "त्रुटि हुई: समय सीमा समाप्त"
        )

    def test_currency_formatting(self):
        """Verify India-specific numbering commas and currency symbols for price formatter."""
        # Test values
        price = 123456.78
        
        # English, Hindi, and Telugu localization formatting checks
        en_fmt = fmt_price(price, "en")
        hi_fmt = fmt_price(price, "hi")
        te_fmt = fmt_price(price, "te")
        
        # Verify symbol and grouping structure
        self.assertIn("₹", en_fmt)
        self.assertIn("₹", hi_fmt)
        self.assertIn("₹", te_fmt)
        
        # India grouping structure check
        self.assertTrue("1,23,456" in en_fmt or "१,२३,४५६" in hi_fmt or "1,23,456" in te_fmt)

    def test_date_formatting(self):
        """Verify date maps correctly to locale-specific month names and characters."""
        test_d = date(2025, 1, 15)
        
        hi_date = fmt_date(test_d, "hi")
        self.assertIn("जन", hi_date) # "जन॰" for January in Hindi
        
        en_date = fmt_date(test_d, "en")
        self.assertIn("Jan", en_date) # "Jan" for January in English

    def test_number_formatting(self):
        """Verify numbers are formatted using locale decimal formats."""
        num = 9876.54
        
        en_num = fmt_number(num, "en")
        self.assertIn("9,876.54", en_num)

    def test_page_render_signatures(self):
        """Verify each page module exposes a callable render function."""
        pages = [crop_advisor_page, weather_page, mandi_page, pest_page, chat_page, schemes_page]
        for page in pages:
            self.assertTrue(hasattr(page, "render"))
            self.assertTrue(callable(getattr(page, "render")))

    def test_clean_json_string_multiple_json(self):
        """Verify clean_json_string parses and extracts only the first valid JSON when multiple objects are returned."""
        from modules.crop_advisor import clean_json_string
        import json
        
        raw_input = (
            '{ "disease_name": "Leaf Rust", "severity": "moderate" }\n\n'
            '{ "disease_name": "Loose Smut", "severity": "severe" }'
        )
        cleaned = clean_json_string(raw_input)
        parsed = json.loads(cleaned)
        self.assertEqual(parsed["disease_name"], "Leaf Rust")
        self.assertEqual(parsed["severity"], "moderate")
        
    def test_format_value_to_string(self):
        """Verify format_value_to_string recursively formats nested types to strings."""
        from modules.pest_diagnosis import format_value_to_string
        
        # Test strings
        self.assertEqual(format_value_to_string(" hello "), "hello")
        
        # Test lists
        self.assertEqual(format_value_to_string(["a", "b"]), "a, b")
        
        # Test dicts
        nested = {
            "Fungicides": ["Mancozeb", "Propiconazole"],
            "Timing": "10-14 days"
        }
        formatted = format_value_to_string(nested)
        self.assertIn("- **Fungicides**: Mancozeb, Propiconazole", formatted)
        self.assertIn("- **Timing**: 10-14 days", formatted)

    def test_localized_severity_and_urgency(self):
        """Verify that severity and urgency displays are localized correctly and return appropriate color codes."""
        from pages.pest_page import get_localized_severity, get_localized_urgency
        
        # Test Telugu severity translations
        disp, color = get_localized_severity("moderate", "te")
        self.assertEqual(disp, "మితమైన")
        self.assertEqual(color, "orange")
        
        disp, color = get_localized_severity("తేలికపాటి", "te")
        self.assertEqual(disp, "తేలికపాటి")
        self.assertEqual(color, "green")
        
        # Test Hindi urgency translations
        disp, color = get_localized_urgency("immediate", "hi")
        self.assertEqual(disp, "तुरंत")
        self.assertEqual(color, "red")

if __name__ == "__main__":
    unittest.main()
