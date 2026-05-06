from flask import Blueprint, render_template, request, session

quiz_bp = Blueprint("quiz", __name__)


@quiz_bp.route("/quiz")
def quiz():
    # Carry UTM through to the form
    utm_source = request.args.get("utm_source", session.get("utm_source", ""))
    utm_campaign = request.args.get("utm_campaign", session.get("utm_campaign", ""))
    session["utm_source"] = utm_source
    session["utm_campaign"] = utm_campaign

    return render_template("quiz.html")
