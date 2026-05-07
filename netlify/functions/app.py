"""
Main Netlify serverless handler — wraps the Flask app via serverless-wsgi.
All HTTP traffic (except /static) is routed here by netlify.toml.
"""
import serverless_wsgi

# Import the Flask application factory
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app import create_app

flask_app = create_app()


def handler(event, context):
    return serverless_wsgi.handle_request(flask_app, event, context)
