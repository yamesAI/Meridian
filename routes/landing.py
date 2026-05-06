from flask import Blueprint, render_template, request

landing_bp = Blueprint("landing", __name__)


@landing_bp.route("/")
def index():
    sign = request.args.get("sign", "").lower()
    lp = request.args.get("lp", "")
    sr = request.args.get("sr", "")
    utm_source = request.args.get("utm_source", "")
    utm_campaign = request.args.get("utm_campaign", "")

    # Build hero variant for targeted landing
    if sr == "1":
        hero_variant = "saturn_return"
    elif sign:
        hero_variant = "sign"
    elif lp:
        hero_variant = "life_path"
    else:
        hero_variant = "default"

    return render_template(
        "landing.html",
        hero_variant=hero_variant,
        sign=sign,
        life_path=lp,
        utm_source=utm_source,
        utm_campaign=utm_campaign,
    )
