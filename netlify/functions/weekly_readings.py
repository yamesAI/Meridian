"""
Netlify Scheduled Function — replaces the PM2 Monday 6am cron.
Schedule: every Monday at 06:00 UTC  →  "0 6 * * 1"

Deploy as a Netlify Scheduled Function by adding to netlify.toml or via
the Netlify dashboard under Functions → Schedule.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from scripts.send_weekly_readings import run


def handler(event, context):
    """Netlify calls this on the configured schedule."""
    run()
    return {"statusCode": 200, "body": "Weekly readings sent"}
