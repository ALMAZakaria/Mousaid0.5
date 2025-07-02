from decimal import Decimal
from datetime import datetime, date

def convert_decimals(obj):
    if isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    else:
        return obj

def convert_currency_to_base(amount, exchange_rate):
    """
    Converts the given amount to the base currency using the provided exchange rate.
    Returns the converted amount rounded to 2 decimals.
    """
    return round(amount * exchange_rate, 2) 