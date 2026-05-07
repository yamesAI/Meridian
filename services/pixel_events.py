import requests
import logging
import hashlib
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

# Map internal event names to platform event names
META_EVENTS = {
    "quiz_start": "InitiateCheckout",
    "quiz_complete": "Lead",
    "free_reading_view": "ViewContent",
    "upgrade_click": "AddToCart",
    "subscription": "Purchase",
}

TIKTOK_EVENTS = {
    "quiz_start": "InitiateCheckout",
    "quiz_complete": "Lead",
    "free_reading_view": "ViewContent",
    "upgrade_click": "AddToCart",
    "subscription": "Purchase",
}


def _hash(value: str) -> str:
    return hashlib.sha256(value.strip().lower().encode()).hexdigest()


def _fire_meta(event_name: str, email: str = "", value: float = 0):
    if not Config.META_PIXEL_ID or not Config.META_ACCESS_TOKEN:
        return

    meta_event = META_EVENTS.get(event_name)
    if not meta_event:
        return

    payload = {
        "data": [
            {
                "event_name": meta_event,
                "event_time": int(datetime.utcnow().timestamp()),
                "event_source_url": Config.BASE_URL,
                "action_source": "website",
                "user_data": {
                    "em": [_hash(email)] if email else [],
                },
                "custom_data": {
                    "value": value,
                    "currency": "USD",
                },
            }
        ]
    }

    try:
        requests.post(
            f"https://graph.facebook.com/v19.0/{Config.META_PIXEL_ID}/events",
            params={"access_token": Config.META_ACCESS_TOKEN},
            json=payload,
            timeout=5,
        )
    except Exception as e:
        logger.warning(f"Meta pixel fire failed: {e}")


def _fire_tiktok(event_name: str, email: str = "", value: float = 0):
    if not Config.TIKTOK_PIXEL_ID or not Config.TIKTOK_ACCESS_TOKEN:
        return

    tiktok_event = TIKTOK_EVENTS.get(event_name)
    if not tiktok_event:
        return

    payload = {
        "pixel_code": Config.TIKTOK_PIXEL_ID,
        "event": tiktok_event,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "context": {
            "user": {
                "email": _hash(email) if email else "",
            },
        },
        "properties": {
            "value": str(value),
            "currency": "USD",
        },
    }

    try:
        requests.post(
            "https://business-api.tiktok.com/open_api/v1.3/pixel/track/",
            headers={
                "Access-Token": Config.TIKTOK_ACCESS_TOKEN,
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=5,
        )
    except Exception as e:
        logger.warning(f"TikTok pixel fire failed: {e}")


def fire_server_event(event_name: str, email: str = "", value: float = 0):
    """Fire server-side conversion event to both Meta and TikTok."""
    _fire_meta(event_name, email, value)
    _fire_tiktok(event_name, email, value)
