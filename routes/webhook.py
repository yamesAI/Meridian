import stripe
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, abort

from config import Config
from app import db
from models.user import User
from services.pixel_events import fire_server_event
from services.email_service import send_welcome_email

stripe.api_key = Config.STRIPE_SECRET_KEY

webhook_bp = Blueprint("webhook", __name__)

PLAN_AMOUNTS = {
    Config.STRIPE_PRICE_PRO: ("pro", 17),
    Config.STRIPE_PRICE_PREMIUM: ("premium", 47),
}


@webhook_bp.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, Config.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        abort(400)

    if event["type"] == "checkout.session.completed":
        _handle_checkout_complete(event["data"]["object"])
    elif event["type"] == "customer.subscription.deleted":
        _handle_subscription_deleted(event["data"]["object"])
    elif event["type"] == "invoice.payment_failed":
        _handle_payment_failed(event["data"]["object"])

    return {"status": "ok"}, 200


def _handle_checkout_complete(session_obj):
    meta = session_obj.get("metadata", {})
    user_id = meta.get("user_id")
    plan = meta.get("plan", "pro")
    customer_id = session_obj.get("customer")
    subscription_id = session_obj.get("subscription")

    user = User.query.get(int(user_id)) if user_id else None
    if not user and session_obj.get("customer_email"):
        user = User.query.filter_by(email=session_obj["customer_email"]).first()

    if not user:
        return

    user.stripe_customer_id = customer_id
    user.stripe_subscription_id = subscription_id
    user.plan = plan
    user.plan_active_until = datetime.utcnow() + timedelta(days=35)
    db.session.commit()

    amount = 17 if plan == "pro" else 47
    fire_server_event("subscription", email=user.email, value=amount)
    send_welcome_email(user)


def _handle_subscription_deleted(sub_obj):
    sub_id = sub_obj.get("id")
    user = User.query.filter_by(stripe_subscription_id=sub_id).first()
    if user:
        user.plan = "free"
        user.plan_active_until = None
        db.session.commit()


def _handle_payment_failed(invoice_obj):
    customer_id = invoice_obj.get("customer")
    user = User.query.filter_by(stripe_customer_id=customer_id).first()
    if user:
        # Mark plan as expired — Stripe will retry automatically
        user.plan_active_until = datetime.utcnow()
        db.session.commit()
