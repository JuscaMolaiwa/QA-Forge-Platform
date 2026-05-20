from flask import Blueprint, jsonify, request
from sqlalchemy import func
from models import TestSession, SessionStatus, Screenshot
from extensions import db

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@reports_bp.get("/summary")
def summary():
    """Aggregate pass/fail/error counts."""
    rows = (
        db.session.query(TestSession.status, func.count(TestSession.id))
        .group_by(TestSession.status)
        .all()
    )
    counts = {status.value: 0 for status in SessionStatus}
    total = 0
    for status, count in rows:
        counts[status.value] = count
        total += count

    pass_rate = (
        round(counts["passed"] / total * 100, 1) if total > 0 else 0.0
    )
    return jsonify({
        "total": total,
        "pass_rate": pass_rate,
        **counts,
    })


@reports_bp.get("/history")
def history():
    """Return recent finished sessions with timing info."""
    limit = min(int(request.args.get("limit", 30)), 100)
    sessions = (
        TestSession.query
        .filter(TestSession.finished_at.isnot(None))
        .order_by(TestSession.finished_at.desc())
        .limit(limit)
        .all()
    )
    return jsonify([s.to_dict() for s in sessions])


@reports_bp.get("/trends")
def trends():
    """Return daily pass/fail counts for the last N days."""
    days = min(int(request.args.get("days", 7)), 30)
    rows = (
        db.session.query(
            func.date(TestSession.finished_at).label("day"),
            TestSession.status,
            func.count(TestSession.id).label("cnt"),
        )
        .filter(TestSession.finished_at.isnot(None))
        .group_by("day", TestSession.status)
        .order_by("day")
        .all()
    )
    trend_map: dict = {}
    for day, status, cnt in rows:
        if day not in trend_map:
            trend_map[day] = {"day": day, "passed": 0, "failed": 0, "error": 0}
        key = status.value if status.value in ("passed", "failed") else "error"
        trend_map[day][key] = cnt

    return jsonify(sorted(trend_map.values(), key=lambda x: x["day"]))


@reports_bp.post("/screenshots")
def save_screenshot():
    """Receive a screenshot from the conftest plugin and store it."""
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id", "").strip()
    image_b64 = data.get("image_b64", "").strip()
    if not session_id or not image_b64:
        return jsonify({"error": "session_id and image_b64 are required"}), 400
    shot = Screenshot(
        session_id=session_id,
        step_name=data.get("step_name", "step"),
        step_index=int(data.get("step_index", 0)),
        image_b64=image_b64,
        passed=data.get("passed"),
    )
    db.session.add(shot)
    db.session.commit()
    return jsonify(shot.to_dict()), 201


@reports_bp.get("/screenshots/<string:session_id>")
def get_screenshots(session_id):
    """Return all screenshots for a session ordered by step index."""
    shots = (
        Screenshot.query
        .filter_by(session_id=session_id)
        .order_by(Screenshot.step_index)
        .all()
    )
    return jsonify([s.to_dict() for s in shots])