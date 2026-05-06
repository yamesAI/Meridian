from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        # Register blueprints
        from routes.landing import landing_bp
        from routes.quiz import quiz_bp
        from routes.reading import reading_bp
        from routes.subscribe import subscribe_bp
        from routes.webhook import webhook_bp
        from routes.blog import blog_bp

        app.register_blueprint(landing_bp)
        app.register_blueprint(quiz_bp)
        app.register_blueprint(reading_bp)
        app.register_blueprint(subscribe_bp)
        app.register_blueprint(webhook_bp)
        app.register_blueprint(blog_bp)

        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=Config.DEBUG)
