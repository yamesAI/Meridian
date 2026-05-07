"""
Netlify Scheduled Function — replaces the PM2 daily 7am cron.
Schedule: every day at 07:00 UTC  →  "0 7 * * *"
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from scripts.saturn_return_check import run


def handler(event, context):
    run()
    return {"statusCode": 200, "body": "Saturn return check complete"}
