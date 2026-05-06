import json
from datetime import datetime

from flask import Blueprint, render_template, request, session, redirect, url_for, flash

from app import db
from models.user import User
from models.reading import Reading
from services.reading_engine import generate_reading
from services.pixel_events import fire_server_event

reading_bp = Blueprint("reading", __name__)


@reading_bp.route("/reading", methods=["POST"])
def create_reading():
    form = request.form

    name = form.get("name", "").strip()
    email = form.get("email", "").strip().lower()
    dob = form.get("dob", "").strip()          # YYYY-MM-DD
    tob = form.get("tob", "").strip()          # HH:MM or empty
    city = form.get("birth_city", "").strip()
    country_code = form.get("country_code", "US").strip()
    focus = form.get("focus", "").strip()

    if not email or not dob or not city:
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("quiz.quiz"))

    # Upsert user
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            email=email,
            name=name,
            dob=datetime.strptime(dob, "%Y-%m-%d").date(),
            tob=tob or None,
            birth_city=city,
            birth_country_code=country_code,
            focus_input=focus,
            utm_source=session.get("utm_source"),
            utm_campaign=session.get("utm_campaign"),
        )
        db.session.add(user)
    else:
        user.focus_input = focus

    db.session.flush()  # get user.id before commit

    try:
        reading_data = generate_reading(
            name=name,
            dob=dob,
            tob=tob,
            city=city,
            country_code=country_code,
            focus=focus,
            reading_type="free_weekly",
        )
    except Exception as e:
        db.session.rollback()
        flash(f"Reading generation failed: {e}", "error")
        return redirect(url_for("quiz.quiz"))

    # Cache key chart fields on the user record
    natal = reading_data.get("_chart_data", {}).get("natal", {})
    saturn = reading_data.get("_chart_data", {}).get("saturn_return", {})
    num = reading_data.get("_chart_data", {}).get("numerology_core", {})

    user.sun_sign = natal.get("sun_sign")
    user.moon_sign = natal.get("moon_sign")
    user.ascendant = natal.get("ascendant")
    user.life_path = num.get("life_path", {}).get("number")
    user.saturn_return_active = saturn.get("in_return", False)
    user.saturn_return_months_remaining = saturn.get("months_remaining")
    user.last_reading_at = datetime.utcnow()

    # Persist reading
    chart_copy = dict(reading_data)
    chart_copy.pop("_chart_data", None)
    record = Reading(
        user_id=user.id,
        reading_type="free_weekly",
        content_json=json.dumps(chart_copy),
        delivered_at=datetime.utcnow(),
    )
    db.session.add(record)
    db.session.commit()

    # Fire conversion pixels
    fire_server_event("free_reading_view", email=email, value=0)

    session["reading_id"] = record.id
    session["user_id"] = user.id

    return redirect(url_for("reading.show_reading", reading_id=record.id))


@reading_bp.route("/reading/<int:reading_id>")
def show_reading(reading_id):
    record = Reading.query.get_or_404(reading_id)
    user = User.query.get(record.user_id)
    reading = json.loads(record.content_json)

    saturn_active = user.saturn_return_active if user else False
    saturn_months = user.saturn_return_months_remaining if user else None

    return render_template(
        "reading.html",
        reading=reading,
        user=user,
        saturn_active=saturn_active,
        saturn_months=saturn_months,
        is_free=(record.reading_type == "free_weekly"),
    )
