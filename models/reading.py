from datetime import datetime
from app import db


class Reading(db.Model):
    __tablename__ = "readings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Type: free_weekly | pro_weekly | premium_monthly | annual_forecast
    reading_type = db.Column(db.String(32), nullable=False)

    # Full JSON blob from Kimi (includes chart_highlights, body, timing_window, etc.)
    content_json = db.Column(db.Text)

    # Delivery
    delivered_at = db.Column(db.DateTime)
    email_sent = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship("User", back_populates="readings")

    def __repr__(self):
        return f"<Reading {self.id} user={self.user_id} type={self.reading_type}>"
