import os
import re
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from extensions import db
from models import TestScript

library_bp = Blueprint("library", __name__, url_prefix="/api/library")

# Directory where .py files on disk are auto-seeded from
TESTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "tests", "sample_tests")


def _safe_filename(name: str) -> str:
    """Slugify a name into a safe .py filename."""
    slug = re.sub(r"[^\w\s-]", "", name.lower())
    slug = re.sub(r"[\s-]+", "_", slug).strip("_")
    if not slug.endswith(".py"):
        slug += ".py"
    return slug


def seed_from_disk():
    """Sync .py files from tests/sample_tests into the DB.
    - New files are inserted.
    - Existing entries are overwritten if the file on disk is newer
      than the DB record's updated_at (disk always wins).
    """
    from utils.logger import get_logger
    logger = get_logger(__name__)

    tests_dir = os.path.abspath(TESTS_DIR)
    if not os.path.isdir(tests_dir):
        return

    changed = 0
    for fname in sorted(os.listdir(tests_dir)):
        if not fname.endswith(".py"):
            continue
        fpath = os.path.join(tests_dir, fname)
        try:
            file_mtime = datetime.fromtimestamp(os.path.getmtime(fpath), tz=timezone.utc)
            with open(fpath, "r") as f:
                content = f.read()
        except OSError:
            continue

        name = fname.replace("_", " ").replace(".py", "").title()
        existing = TestScript.query.filter_by(filename=fname).first()

        if existing is None:
            db.session.add(TestScript(
                name=name, filename=fname, content=content,
                description=f"Imported from tests/sample_tests/{fname}",
                platform="android",
            ))
            logger.info("Seeded new script: %s", fname)
            changed += 1
        else:
            db_updated = existing.updated_at
            if db_updated.tzinfo is None:
                db_updated = db_updated.replace(tzinfo=timezone.utc)
            if file_mtime > db_updated:
                existing.content = content
                existing.updated_at = datetime.now(timezone.utc)
                logger.info("Re-seeded updated script: %s (disk newer by %.1fs)",
                            fname, (file_mtime - db_updated).total_seconds())
                changed += 1

    db.session.commit()
    logger.info("seed_from_disk: %d script(s) synced", changed)


# ── Routes ────────────────────────────────────────────────────────────────────

@library_bp.get("/")
def list_scripts():
    """List all saved test scripts (no content body — fast for the browser panel)."""
    platform = request.args.get("platform")
    tag = request.args.get("tag")
    q = TestScript.query.order_by(TestScript.updated_at.desc())
    if platform:
        q = q.filter_by(platform=platform.lower())
    scripts = q.all()
    if tag:
        scripts = [s for s in scripts if tag in (s.tags or "")]
    return jsonify([s.to_dict(include_content=False) for s in scripts])


@library_bp.get("/<int:script_id>")
def get_script(script_id):
    script = TestScript.query.get_or_404(script_id, description="Script not found")
    return jsonify(script.to_dict(include_content=True))


@library_bp.post("/")
def create_script():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    content = data.get("content", "").strip()
    if not name:
        return jsonify({"error": "'name' is required"}), 400
    if not content:
        return jsonify({"error": "'content' is required"}), 400

    filename = _safe_filename(name)
    # Ensure filename is unique
    base, ext = filename[:-3], ".py"
    counter = 1
    while TestScript.query.filter_by(filename=filename).first():
        filename = f"{base}_{counter}{ext}"
        counter += 1

    script = TestScript(
        name=name,
        filename=filename,
        content=content,
        description=data.get("description", ""),
        platform=data.get("platform", "android").lower(),
        tags=",".join(data.get("tags", [])) if isinstance(data.get("tags"), list) else data.get("tags", ""),
    )
    db.session.add(script)
    db.session.commit()
    return jsonify(script.to_dict()), 201


@library_bp.put("/<int:script_id>")
def update_script(script_id):
    script = TestScript.query.get_or_404(script_id, description="Script not found")
    data = request.get_json(silent=True) or {}
    if "name" in data and data["name"].strip():
        script.name = data["name"].strip()
    if "content" in data and data["content"].strip():
        script.content = data["content"].strip()
    if "description" in data:
        script.description = data["description"]
    if "platform" in data:
        script.platform = data["platform"].lower()
    if "tags" in data:
        tags = data["tags"]
        script.tags = ",".join(tags) if isinstance(tags, list) else tags
    script.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify(script.to_dict())


@library_bp.delete("/<int:script_id>")
def delete_script(script_id):
    script = TestScript.query.get_or_404(script_id, description="Script not found")
    db.session.delete(script)
    db.session.commit()
    return jsonify({"message": f"Deleted '{script.name}'"})


@library_bp.post("/upload")
def upload_script():
    """Accept a .py file upload and save it to the library."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f = request.files["file"]
    if not f.filename.endswith(".py"):
        return jsonify({"error": "Only .py files are accepted"}), 400
    content = f.read().decode("utf-8", errors="replace")
    name = f.filename.replace("_", " ").replace(".py", "").title()
    filename = _safe_filename(name)
    base, ext = filename[:-3], ".py"
    counter = 1
    while TestScript.query.filter_by(filename=filename).first():
        filename = f"{base}_{counter}{ext}"
        counter += 1
    script = TestScript(name=name, filename=filename, content=content, platform="android")
    db.session.add(script)
    db.session.commit()
    return jsonify(script.to_dict()), 201
