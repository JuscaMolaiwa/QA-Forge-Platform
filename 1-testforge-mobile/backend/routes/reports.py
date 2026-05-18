from flask import Blueprint, jsonify, request
from sqlalchemy import func
from models import TestSession, SessionStatus
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
    # Build a day → {passed, failed} map
    trend_map: dict = {}
    for day, status, cnt in rows:
        if day not in trend_map:
            trend_map[day] = {"day": day, "passed": 0, "failed": 0, "error": 0}
        key = status.value if status.value in ("passed", "failed") else "error"
        trend_map[day][key] = cnt

    return jsonify(sorted(trend_map.values(), key=lambda x: x["day"]))
