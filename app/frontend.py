from datetime import date, datetime
from decimal import Decimal

from django.contrib.messages import get_messages
from django.middleware.csrf import get_token
from django.shortcuts import render


def serialize(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {str(key): serialize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [serialize(item) for item in value]
    if hasattr(value, "_meta"):
        return {
            field.attname: serialize(getattr(value, field.attname))
            for field in value._meta.concrete_fields
        }
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"Cannot serialize frontend value of type {type(value).__name__}")


def render_react(request, page, props=None, status=200, body_class=""):
    serialized_props = serialize(props or {})
    messages = [(message.tags, str(message)) for message in get_messages(request)]
    csrf_token = get_token(request)
    return render(
        request,
        "react.html",
        {
            "page": page,
            "props": serialized_props,
            "title": serialized_props.get("title", "Fieldnote"),
            "bootstrap": {
                "page": page,
                "props": serialized_props,
                "flashes": messages,
                "csrfToken": csrf_token,
            },
            "flash_messages": messages,
            "csrf_token": csrf_token,
            "invite_url": serialized_props.get("invite_url"),
            "body_class": body_class,
        },
        status=status,
    )
