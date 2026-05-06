import logging
import resend
from config import Config

logger = logging.getLogger(__name__)

resend.api_key = Config.RESEND_API_KEY

BASE_URL = Config.BASE_URL
FROM = f"{Config.FROM_NAME} <{Config.FROM_EMAIL}>"


def _send(to: str, subject: str, html: str):
    try:
        resend.Emails.send({
            "from": FROM,
            "to": [to],
            "subject": subject,
            "html": html,
        })
        logger.info(f"Email sent to {to}: {subject}")
    except Exception as e:
        logger.error(f"Email failed to {to}: {e}")


def send_welcome_email(user):
    """Day 0: Welcome + reading ready notification."""
    name = user.name or "there"
    html = f"""
<div style="font-family:Georgia,serif;max-width:600px;margin:0 auto;color:#e8e4d8;background:#08080f;padding:40px 32px;">
  <p style="color:#c9a84c;letter-spacing:0.15em;font-size:13px;text-transform:uppercase;">✦ The Meridian</p>
  <h1 style="font-size:28px;margin:16px 0;">Welcome, {name}.</h1>
  <p style="line-height:1.8;color:#8a8778;">Your transit reading is ready. This is not a template — it was generated specifically for your chart, your profection year, and your current transits.</p>
  <p style="line-height:1.8;color:#8a8778;">Over the next two weeks, I'll send you three more dispatches:</p>
  <ul style="color:#8a8778;line-height:2;">
    <li>Day 2: The technique behind your reading (profection year explained)</li>
    <li>Day 4: What William Lilly wrote about your Saturn Return</li>
    <li>Day 8: Your timing windows for the month ahead</li>
  </ul>
  <a href="{BASE_URL}/subscribe?plan=pro" style="display:inline-block;background:#c9a84c;color:#08080f;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:600;margin-top:24px;">
    Unlock Full Weekly Readings — $17/mo →
  </a>
  <p style="margin-top:40px;font-size:12px;color:#4a4840;">The Meridian · Rooted in 700 years of traditional astrology · <a href="{BASE_URL}/unsubscribe" style="color:#4a4840;">Unsubscribe</a></p>
</div>
"""
    _send(user.email, "Your transit reading is ready", html)


def send_reading_email(user, reading_data: dict, reading_id: int):
    """Weekly reading delivery email."""
    name = user.name or "there"
    title = reading_data.get("title", "Your Weekly Transit Reading")
    hook = reading_data.get("hook", "")
    urgency = reading_data.get("urgency_flag", "")
    body_preview = reading_data.get("body", "")[:400] + "…"
    reading_url = f"{BASE_URL}/reading/{reading_id}"

    html = f"""
<div style="font-family:Georgia,serif;max-width:600px;margin:0 auto;color:#e8e4d8;background:#08080f;padding:40px 32px;">
  <p style="color:#c9a84c;letter-spacing:0.15em;font-size:13px;text-transform:uppercase;">✦ The Meridian · Weekly Dispatch</p>
  <h1 style="font-size:26px;margin:16px 0;">{title}</h1>
  <blockquote style="border-left:3px solid #c9a84c;padding:12px 20px;background:rgba(201,168,76,0.04);font-style:italic;color:#e8e4d8;margin:24px 0;">
    {hook}
  </blockquote>
  {"<p style='background:rgba(201,168,76,0.08);border:1px solid #7a6330;padding:12px 16px;border-radius:8px;font-size:14px;color:#8a8778;'>⚡ " + urgency + "</p>" if urgency else ""}
  <p style="line-height:1.8;color:#8a8778;">{body_preview}</p>
  <a href="{reading_url}" style="display:inline-block;background:#c9a84c;color:#08080f;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:600;margin-top:24px;">
    Read Your Full Reading →
  </a>
  <p style="margin-top:40px;font-size:12px;color:#4a4840;">The Meridian · <a href="{BASE_URL}/unsubscribe" style="color:#4a4840;">Manage subscription</a></p>
</div>
"""
    _send(user.email, f"✦ {title}", html)


def send_saturn_return_alert(user, saturn_data: dict):
    """Alert email for newly flagged Saturn Return users."""
    name = user.name or "there"
    months = saturn_data.get("months_remaining", "")
    themes = ", ".join(saturn_data.get("themes", [])[:3])
    interpretation = saturn_data.get("interpretation", "")[:300]

    html = f"""
<div style="font-family:Georgia,serif;max-width:600px;margin:0 auto;color:#e8e4d8;background:#08080f;padding:40px 32px;">
  <p style="color:#c9a84c;letter-spacing:0.15em;font-size:13px;text-transform:uppercase;">♄ Saturn Return Alert</p>
  <h1 style="font-size:26px;margin:16px 0;">{name}, your Saturn Return is active.</h1>
  {"<p style='color:#8a8778;'>Approximately <strong style='color:#e8e4d8;'>" + str(months) + " months remaining</strong> in this window.</p>" if months else ""}
  {"<p style='color:#8a8778;'>Current themes: <em>" + themes + "</em></p>" if themes else ""}
  <p style="line-height:1.8;color:#8a8778;">{interpretation}</p>
  <p style="line-height:1.8;color:#8a8778;">William Lilly wrote in 1647 that Saturn's return marks <em>"the completion of the first great arc of a man's life."</em> This window is finite. Knowing where you are in it — and what the transits are doing inside it — changes what's available to you.</p>
  <a href="{BASE_URL}/subscribe?plan=pro&utm_source=saturn_alert" style="display:inline-block;background:#c9a84c;color:#08080f;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:600;margin-top:24px;">
    Get Your Full Saturn Return Analysis →
  </a>
  <p style="margin-top:40px;font-size:12px;color:#4a4840;">The Meridian · <a href="{BASE_URL}/unsubscribe" style="color:#4a4840;">Unsubscribe</a></p>
</div>
"""
    _send(user.email, "♄ Your Saturn Return is active", html)
