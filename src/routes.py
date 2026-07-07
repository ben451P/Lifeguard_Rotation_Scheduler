import os
from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime, timezone

from backend.scheduler import Scheduler
from backend.utils import minutes_to_time, time_to_minutes
from backend.xlsx_writer import XLSXWriter
from debug.logger import Logger
from debug.report import Report
from src.config import EXAMPLE_PASSWORD, EXAMPLE_USERNAME
from src.extensions import db
from src.models import BugReport, Preferences, User


main = Blueprint("main", __name__, template_folder="templates")


@main.route("/")
@login_required
def index():
    return render_template("index.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("User does not exist", "warning")
            return redirect(url_for("main.login"))

        if user.password.strip() == password.strip():
            login_user(user)
            flash("Successfully logged in", "success")
        return redirect(url_for("main.index"))
    return render_template("login.html")


@main.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@main.route("/fixed-vars", methods=["GET", "POST"])
@login_required
def fixed_vars():
    preferences = Preferences.query.filter_by(account=current_user.id).first()
    if request.method == "POST":
        preferences.schedule_start = request.form.get("Start Time")
        preferences.schedule_end = request.form.get("End Time")
        preferences.acceptable_lunch_start = request.form.get("Lunch Start Time")
        preferences.acceptable_lunch_end = request.form.get("Lunch End Time")
        db.session.commit()

    starts_and_ends = {
        "Start Time": preferences.schedule_start,
        "End Time": preferences.schedule_end,
        "Lunch Start Time": preferences.acceptable_lunch_start,
        "Lunch End Time": preferences.acceptable_lunch_end,
    }

    coverage_times = preferences.station_coverage_times
    return render_template("fixed_vars.html", vars_list=starts_and_ends, coverage_times=coverage_times)


@main.route("/rotation-cycle", methods=["GET", "POST"])
@login_required
def rotation_cycle():
    preferences = Preferences.query.filter_by(account=current_user.id).first()
    if request.method == "POST":
        ids = request.form.getlist("station_id[]")
        names = request.form.getlist("station_name[]")

        if len(ids) != len(names):
            flash("Submitted data malformed (ids and names mismatch).", "danger")
            return redirect(url_for("main.rotation_cycle"))

        if len(set(names)) != len(names):
            flash("Cannot have 2 stations with the same name!", "danger")
            return redirect(url_for("main.rotation_cycle"))

        old_cycle = preferences.rotation_cycle or []
        station_importance = preferences.station_importance or []

        old_map = {}
        for item in old_cycle:
            if isinstance(item, dict):
                old_map[item.get("id", item.get("name"))] = item.get("name")
            else:
                old_map[item] = item

        new_cycle_dicts = []
        for sid, sname in zip(ids, names):
            name = (sname or "").strip() or "New Station"

            old_name = old_map.get(sid, sid)
            if name != old_name:
                if old_name in station_importance:
                    station_importance = [name if x == old_name else x for x in station_importance]
                else:
                    if name not in station_importance:
                        station_importance.insert(0, name)

            new_cycle_dicts.append({"id": sid, "name": name})

        if not new_cycle_dicts:
            flash("Cannot save empty rotation. Add at least one station.", "warning")
            return redirect(url_for("main.rotation_cycle"))

        new_names = [d["name"] for d in new_cycle_dicts]
        station_importance = [x for x in station_importance if x in new_names]

        preferences.station_importance = station_importance.copy()
        preferences.rotation_cycle = new_names.copy()
        flag_modified(preferences, "station_importance")

        try:
            db.session.commit()
            flash("Rotation saved.", "success")
        except Exception:
            db.session.rollback()
            current_app.logger.exception("Failed saving rotation cycle")
            flash("Failed to save rotation cycle.", "danger")

        return redirect(url_for("main.rotation_cycle"))

    cycles = preferences.rotation_cycle or []
    if cycles and isinstance(cycles[0], str):
        cycles = [{"id": c, "name": c} for c in cycles]

    return render_template("rotation_cycle.html", cycles=cycles)


@main.route("/importance", methods=["GET", "POST"])
@login_required
def importance():
    preferences = Preferences.query.filter_by(account=current_user.id).first()

    if request.method == "POST":
        new_order = request.form.getlist("station_id[]")

        if not new_order:
            flash("No stations received. Nothing saved.", "warning")
            return redirect(url_for("main.importance"))

        new_order = new_order[::-1]

        preferences.station_importance = new_order
        try:
            db.session.commit()
            flash("Rotation order saved.", "success")
        except Exception:
            db.session.rollback()
            current_app.logger.exception("Failed saving rotation order")
            flash("Failed to save rotation order.", "danger")

        return redirect(url_for("main.importance"))

    cycles = preferences.station_importance[::-1] or []
    return render_template("importance.html", cycles=cycles)


@main.route("/shifts", methods=["GET", "POST"])
@login_required
def shifts():
    preferences = Preferences.query.filter_by(account=current_user.id).first()
    if request.method == "POST":
        guard_names = request.form.getlist("guard_name[]")
        start_times = request.form.getlist("start_time[]")
        end_times = request.form.getlist("end_time[]")

        attendance = [i == "true" for i in request.form.getlist("attendance[]")]
        lunch_break = [i == "true" for i in request.form.getlist("lunch_break[]")]

        for i in range(len(start_times)):
            if time_to_minutes(start_times[i]) > time_to_minutes(end_times[i]):
                flash("All start times must be before end times", "danger")
                return redirect(url_for("main.shifts"))

        shifts = [[g, s, e, a, lb] for g, s, e, a, lb in zip(guard_names, start_times, end_times, attendance, lunch_break)]
        preferences.shifts = shifts
        flag_modified(preferences, "shifts")
        try:
            db.session.commit()
            flash("Rotation order saved.", "success")
        except Exception:
            db.session.rollback()
            current_app.logger.exception("Failed saving new shifts")
            flash("Failed to save rotation order.", "danger")
        return redirect(url_for("main.shifts"))

    shifts_list = preferences.shifts or []
    return render_template("shifts.html", shifts_list=shifts_list, enumerate=enumerate)


@main.route("/generate_schedule", methods=["POST"])
@login_required
def generate_schedule():
    preferences = Preferences.query.filter_by(account=current_user.id).first()

    start = preferences.schedule_start
    end = preferences.schedule_end
    lunch_start = preferences.acceptable_lunch_start
    lunch_end = preferences.acceptable_lunch_end

    lunch_end = time_to_minutes(lunch_end) - 60
    lunch_end = minutes_to_time(lunch_end)

    cycle = preferences.rotation_cycle
    importance = preferences.station_importance
    coverage_times = {i: [("11:00", "20:00")] for i in cycle}
    shifts = [[a, b, c] if d else [a, "00:00", "00:00"] for a, b, c, d, _ in preferences.shifts]
    lunches = [e for _, _, _, _, e in preferences.shifts]

    scheduler = Scheduler(start, end, lunch_start, lunch_end, cycle, importance, coverage_times, shifts)
    scheduler.manually_override_lunches(lunches)
    scheduler.schedule_lunches()
    scheduler.create_base_schedule()

    writer = XLSXWriter(scheduler)
    excel_file = writer.convert_to_excel()

    return send_file(
        excel_file,
        as_attachment=True,
        download_name="schedule.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@main.route("/report_bug", methods=["POST"])
def report_bug():
    bug_desc = request.form.get("bug_description")
    time = datetime.now(timezone.utc)

    bug_report = BugReport(
        report_user_id=current_user.id,
        bug_description=bug_desc,
        time_stamp=time,
    )
    db.session.add(bug_report)
    db.session.commit()

    bug_report = BugReport.query.filter_by(time_stamp=time).first()

    report = Report(bug_report)
    report.fetch_account_state(db, Preferences)

    logger = Logger(current_app.config["LOG_PATH"])
    logger.write_report(report)

    flash("System architect notified of bug", "success")
    return redirect(url_for("main.index"))


@main.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404


@main.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("500.html"), 500
