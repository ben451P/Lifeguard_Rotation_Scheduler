import os
from pathlib import Path

from flask import Flask

from src.config import LOG_PATH, ROTATION_CYCLE, SHIFTS, STATION_IMPORTANCE_DESCENDING, EXAMPLE_PASSWORD, EXAMPLE_USERNAME
from src.extensions import db, login_manager
from src.models import Preferences, User
from src.routes import main


def create_app(config_overrides=None):
    base_dir = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(base_dir / "templates"),
        static_folder=str(base_dir / "static"),
    )

    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///app.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER="uploads",
        PROCESSED_FOLDER="processed",
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
        LOG_PATH=LOG_PATH,
    )

    if config_overrides:
        app.config.update(config_overrides)

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(main)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        initialize_default_data()

    return app


def initialize_default_data():
    demo_user = User.query.first()
    if not demo_user:
        user = User(email=EXAMPLE_USERNAME, password=EXAMPLE_PASSWORD)
        db.session.add(user)
        db.session.commit()

        preferences = Preferences(
            account=user.id,
            schedule_start="11:00",
            schedule_end="19:30",
            acceptable_lunch_start="13:00",
            acceptable_lunch_end="16:00",
            rotation_cycle=ROTATION_CYCLE["data"],
            station_importance=STATION_IMPORTANCE_DESCENDING["data"],
            shifts=SHIFTS["data"],
        )
        db.session.add(preferences)
        db.session.commit()


app = create_app()
