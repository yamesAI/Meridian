import stripe
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from config import Config
from app import db
from models.user import User
from services.pixel_events import fire_server_event

stripe.api_key = Config.STRIPE_SECRET_KEY

subscribe_bp = Blueprint("subscribe", __name__)


@subscribe_bp.route("/subscribe")
def subscribe():
    plan = request.args.get("plan", "pro")
    user_id = session.get("user_id")
    user = User.query.get(user_id) if user_id else None
    return render_template("subscribe.html", plan=plan, user=user)


@subscribe_bp.route("/checkout", methods=["POST"])
def checkout():
    plan = request.form.get("plan", "pro")
    user_id = session.get("user_id")

    price_id = (
        Config.STRIPE_PRICE_PREMIUM if plan == "premium" else Config.STRIPE_PRICE_PRO
    )

    user = User.query.get(user_id) if user_id else None
    customer_email = user.email if user else request.form.get("email", "")

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            customer_email=customer_email if not (user and user.stripe_customer_id) else None,
            customer=user.stripe_customer_id if user and user.stripe_customer_id else None,
            success_url=Config.BASE_URL + "/subscribe/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=Config.BASE_URL + "/subscribe",
            metadata={"user_id": str(user_id) if user_id else "", "plan": plan},
        )
        if user:
            fire_server_event("upgrade_click", email=user.email, value=17 if plan == "pro" else 47)
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f"Checkout error: {e}", "error")
        return redirect(url_for("subscribe.subscribe"))


@subscribe_bp.route("/subscribe/success")
def success():
    session_id = request.args.get("session_id")
    return render_template("subscribe_success.html", session_id=session_id)
