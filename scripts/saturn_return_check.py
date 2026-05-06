#!/usr/bin/env python3
"""
Cron: daily Saturn Return flag refresh.
Runs every day at 7:00 AM UTC via PM2.
Flags users entering the Saturn Return window and sends alert emails.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from datetime import datetime

from app import create_app, db
from models.user import User
from services.astrology_api import AstrologyAPI
from services.email_service import send_saturn_return_alert
from config import Config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

api = AstrologyAPI(Config.ASTROLOGY_API_KEY)


def run():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        logger.info(f"Checking Saturn Return status for {len(users)} users")

        for user in users:
            try:
                dob = user.dob.strftime("%Y-%m-%d")
                sr = api.saturn_return(
                    name=user.name or "",
                    dob=dob,
                    tob=user.tob or "",
                    city=user.birth_city or "",
                    country_code=user.birth_country_code or "US",
                )

                was_active = user.saturn_return_active
                now_active = sr.get("in_return", False)
                months_remaining = sr.get("months_remaining")

                user.saturn_return_active = now_active
                user.saturn_return_months_remaining = months_remaining

                # Newly flagged — send alert
                if not was_active and now_active:
                    logger.info(f"Saturn Return NEWLY active for {user.email}")
                    send_saturn_return_alert(user, sr)

                db.session.commit()

            except Exception as e:
                db.session.rollback()
                logger.error(f"Failed for {user.email}: {e}")


if __name__ == "__main__":
    run()
