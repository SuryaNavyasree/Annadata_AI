"""
utils/l10n.py

Localization utility to format currency, dates, and decimal numbers using the babel library
according to target languages.
"""

from datetime import date, datetime
import babel.numbers
import babel.dates

def _get_babel_locale(lang: str) -> str:
    """
    Maps application language codes to India-specific babel locales.
    """
    if lang == "hi":
        return "hi_IN"
    elif lang == "te":
        return "te_IN"
    return "en_IN"

def fmt_price(amount: float, lang: str) -> str:
    """
    Formats the numeric amount as Indian Rupees (INR) using India-specific numbering rules.

    Parameters:
        amount (float): The price amount.
        lang (str): Language code ("en", "hi", "te").

    Returns:
        str: Formatted price string (e.g. ₹1,23,456.00).
    """
    try:
        if amount is None:
            amount = 0.0
        amount = float(amount)
        locale_code = _get_babel_locale(lang)
        # format_currency automatically handles the currency symbol and commas formatting
        return babel.numbers.format_currency(amount, 'INR', locale=locale_code)
    except Exception:
        return f"₹{amount}"

def fmt_date(d: date, lang: str) -> str:
    """
    Formats the date to the locale script.

    Parameters:
        d (date): The date object or ISO string.
        lang (str): Language code ("en", "hi", "te").

    Returns:
        str: Formatted date string (e.g. "15 जन॰ 2025").
    """
    try:
        if isinstance(d, str):
            # Try parsing if date is passed as string
            try:
                d = datetime.strptime(d, "%Y-%m-%d").date()
            except ValueError:
                d = datetime.strptime(d, "%d/%m/%Y").date()
        locale_code = _get_babel_locale(lang)
        return babel.dates.format_date(d, format='medium', locale=locale_code)
    except Exception:
        return str(d)

def fmt_number(n: float, lang: str) -> str:
    """
    Formats a decimal number for the locale.

    Parameters:
        n (float): The number.
        lang (str): Language code ("en", "hi", "te").

    Returns:
        str: Formatted number string.
    """
    try:
        if n is None:
            n = 0.0
        n = float(n)
        locale_code = _get_babel_locale(lang)
        return babel.numbers.format_decimal(n, locale=locale_code)
    except Exception:
        return str(n)
