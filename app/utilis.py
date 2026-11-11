import re
from datetime import datetime

def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:80]

def format_currency(value):
    return f"${value:,.2f}"

def current_timestamp():
    return datetime.utcnow()