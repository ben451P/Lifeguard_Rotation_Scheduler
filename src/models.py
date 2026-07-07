from datetime import datetime, timezone

from flask_login import UserMixin
from sqlalchemy import JSON

from src.extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    preferences = db.relationship("Preferences", backref="user", lazy = True)

class Preferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    schedule_start = db.Column(db.String)
    schedule_end = db.Column(db.String)
    acceptable_lunch_start = db.Column(db.String)
    acceptable_lunch_end = db.Column(db.String)

    rotation_cycle = db.Column(JSON) #, default=load_default_rotation
    station_importance = db.Column(JSON) #, default=load_default_importance
    station_coverage_times = db.Column(JSON)
    shifts = db.Column(JSON)

class BugReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_user_id = db.Column(db.Integer)
    time_stamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    bug_description = db.Column(db.String)
    resolved = db.Column(db.Boolean, default=False)