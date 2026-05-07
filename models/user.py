from datetime import datetime
from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255))

    # Birth data
    dob = db.Column(db.Date, nullable=False)
    tob = db.Column(db.String(5))           # "HH:MM" — nullable if unknown
    birth_city = db.Column(db.String(255))
    birth_country_code = db.Column(db.String(4))
    birth_lat = db.Column(db.Float)
    birth_lon = db.Column(db.Float)
    birth_tz = db.Column(db.String(64))

    # Cached chart data — computed at signup
    sun_sign = db.Column(db.String(32))
    moon_sign = db.Column(db.String(32))
    ascendant = db.Column(db.String(32))
    life_path = db.Column(db.Integer)
    saturn_return_active = db.Column(db.Boolean, default=False)
    saturn_return_months_remaining = db.Column(db.Integer)

    # Subscription
    stripe_customer_id = db.Column(db.String(255))
    stripe_subscription_id = db.Column(db.String(255))
    plan = db.Column(db.String(32), default="free")   # free | pro | premium
    plan_active_until = db.Column(db.DateTime)

    # UTM / acquisition tracking
    utm_source = db.Column(db.String(128))
    utm_medium = db.Column(db.String(128))
    utm_campaign = db.Column(db.String(128))

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_reading_at = db.Column(db.DateTime)

    # Focus input from quiz
    focus_input = db.Column(db.Text)

    # Relationship
    readings = db.relationship("Reading", back_populates="user", lazy="dynamic")

    def is_subscribed(self) -> bool:
        if self.plan == "free":
            return False
        if self.plan_active_until and self.plan_active_until > datetime.utcnow():
            return True
        return False

    def __repr__(self):
        return f"<User {self.email} plan={self.plan}>"
