#!/usr/bin/env python3
"""
Cron: send weekly readings to all active Pro/Premium subscribers.
Runs every Monday at 6:00 AM UTC via PM2.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import logging
from datetime import datetime

from app import create_app, db
from models.user import User
from models.reading import Reading
from services.reading_engine import generate_reading
from services.email_service import send_reading_email

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run():
    app = create_app()
    with app.app_context():
        users = User.query.filter(
            User.plan.in_(["pro", "premium"]),
            User.plan_active_until > datetime.utcnow(),
        ).all()

        logger.info(f"Sending weekly readings to {len(users)} subscribers")

        for user in users:
            try:
                reading_type = (
                    "pro_weekly" if user.plan == "pro" else "premium_monthly"
                )
                dob = user.dob.strftime("%Y-%m-%d")
                reading_data = generate_reading(
                    name=user.name or "",
                    dob=dob,
                    tob=user.tob or "",
                    city=user.birth_city or "",
                    country_code=user.birth_country_code or "US",
                    focus=user.focus_input or "",
                    reading_type=reading_type,
                )

                chart_copy = dict(reading_data)
                chart_copy.pop("_chart_data", None)

                record = Reading(
                    user_id=user.id,
                    reading_type=reading_type,
                    content_json=json.dumps(chart_copy),
                    delivered_at=datetime.utcnow(),
                )
                db.session.add(record)
                db.session.flush()

                send_reading_email(user, reading_data, record.id)
                record.email_sent = True
                user.last_reading_at = datetime.utcnow()

                db.session.commit()
                logger.info(f"Reading sent to {user.email}")

            except Exception as e:
                db.session.rollback()
                logger.error(f"Failed for {user.email}: {e}")


if __name__ == "__main__":
    run()
