from flask import Blueprint, jsonify, request, current_app
from models import TestSession, SessionStatus
from services.test_executor import create_session
from utils.validators import validate_test_payload
from extensions import db

tests_bp = Blueprint("tests", __name__, url_prefix="/api/tests")


def _queue():
    return current_app.queue_manager


@tests_bp.post("/")
def submit_test():
    data = request.get_json(silent=True) or {}
    ok, msg = validate_test_payload(data)
    if not ok:
        return jsonify({"error": msg}), 400

    session = create_session(
        test_name=data["test_name"],
        test_content=data.get("test_content", ""),
        test_file=data.get("test_file", ""),
        app_path=data.get("app_path", ""),
    )

    if not _queue().enqueue(session.session_id):
        session.status = SessionStatus.ERROR
        session.error_message = "Queue is full — try again later"
        from extensions import db
        db.session.commit()
        return jsonify({"error": "Queue is full"}), 503

    return jsonify(session.to_dict()), 202


@tests_bp.get("/")
def list_sessions():
    status_filter = request.args.get("status")
    query = TestSession.query.order_by(TestSession.queued_at.desc())
    if status_filter:
        try:
            status_enum = SessionStatus(status_filter)
            query = query.filter_by(status=status_enum)
        except ValueError:
            return jsonify({"error": f"Invalid status '{status_filter}'"}), 400
    limit = min(int(request.args.get("limit", 50)), 200)
    sessions = query.limit(limit).all()
    return jsonify([s.to_dict() for s in sessions])


@tests_bp.get("/<string:session_id>")
def get_session(session_id):
    session = TestSession.query.filter_by(session_id=session_id).first()
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(session.to_dict())


@tests_bp.delete("/<string:session_id>")
def cancel_session(session_id):
    session = TestSession.query.filter_by(session_id=session_id).first()
    if not session:
        return jsonify({"error": "Session not found"}), 404
    if session.status == SessionStatus.RUNNING:
        return jsonify({"error": "Cannot cancel a running session"}), 409
    removed = _queue().remove(session_id)
    if removed or session.status == SessionStatus.QUEUED:
        session.status = SessionStatus.CANCELLED
        from extensions import db
        db.session.commit()
    return jsonify(session.to_dict())


@tests_bp.get("/queue/status")
def queue_status():
    q = _queue()
    return jsonify({
        "depth": q.depth(),
        "pending": q.snapshot(),
    })

@tests_bp.post("/process")
def process_queue():
    """Trigger one queue cycle — workaround for free tier background thread limits."""
    import threading

    session_id = current_app.queue_manager.dequeue()
    if not session_id:
        return jsonify({"message": "Queue empty"}), 200

    def run():
        with current_app.app_context():
            db.session.remove()
            current_app.test_executor._execute(session_id)

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"message": f"Processing {session_id}"}), 202
