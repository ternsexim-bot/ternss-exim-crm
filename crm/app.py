import logging
import os

from flask import Flask, jsonify, request
from flask_cors import CORS

try:
    from crm.models import db, Lead   # crm.app:app from repo root
except ImportError:
    from models import db, Lead       # app:app from crm/ directory

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# ── Database configuration (optional — app boots without it) ──────────────────

_DATABASE_URL = os.getenv("DATABASE_URL", "")

# Render supplies postgres:// shorthand — normalise to postgresql://
if _DATABASE_URL.startswith("postgres://"):
    _DATABASE_URL = _DATABASE_URL.replace("postgres://", "postgresql://", 1)

# psycopg2 is incompatible with Python 3.14 — use psycopg3 dialect
if _DATABASE_URL.startswith("postgresql://"):
    _DATABASE_URL = _DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

if _DATABASE_URL:
    app.config["SQLALCHEMY_DATABASE_URI"] = _DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    _DB_LABEL = "postgresql"
    print("[STARTUP] DATABASE_URL detected — using PostgreSQL")
else:
    logger.warning("[STARTUP] DATABASE_URL not set — running without database")
    _DB_LABEL = "not_connected"
    print("[STARTUP] WARNING: DATABASE_URL not set — database features unavailable")

# Create tables only when a real DB is configured
if _DATABASE_URL:
    try:
        with app.app_context():
            db.create_all()
            print("[STARTUP] Connected to PostgreSQL — tables verified.")
    except Exception as exc:
        logger.error("[STARTUP] DB table creation failed: %s", exc)
        _DB_LABEL = "not_connected"
        print("[STARTUP] WARNING: Could not reach database at startup:", exc)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "database": _DB_LABEL,
        "persistent": _DB_LABEL == "postgresql",
    })


def _db_unavailable():
    return jsonify({"error": "Database not configured"}), 503


@app.route("/leads", methods=["GET"])
def get_leads():
    if not _DATABASE_URL:
        return _db_unavailable()
    status = request.args.get("status")
    query = Lead.query.order_by(Lead.created_at.desc())
    if status:
        query = query.filter_by(status=status)
    return jsonify([lead.to_dict() for lead in query.all()])


@app.route("/leads", methods=["POST"])
def create_lead():
    if not _DATABASE_URL:
        return _db_unavailable()
    data = request.get_json() or {}
    if not data.get("name", "").strip():
        return jsonify({"error": "Name is required"}), 400
    lead = Lead(
        name=data.get("name", "").strip(),
        email=data.get("email", ""),
        phone=data.get("phone", ""),
        company=data.get("company", ""),
        country=data.get("country", ""),
        product_interest=data.get("product_interest", ""),
        message=data.get("message", ""),
        status=data.get("status", "New"),
        source=data.get("source", "Website"),
    )
    db.session.add(lead)
    db.session.commit()
    return jsonify(lead.to_dict()), 201


@app.route("/leads/<int:lead_id>", methods=["PUT"])
def update_lead(lead_id):
    if not _DATABASE_URL:
        return _db_unavailable()
    lead = db.get_or_404(Lead, lead_id)
    data = request.get_json() or {}
    updatable = ["name", "email", "phone", "company", "country",
                 "product_interest", "message", "status", "source"]
    for field in updatable:
        if field in data:
            setattr(lead, field, data[field])
    db.session.commit()
    return jsonify(lead.to_dict())


@app.route("/leads/<int:lead_id>", methods=["DELETE"])
def delete_lead(lead_id):
    if not _DATABASE_URL:
        return _db_unavailable()
    lead = db.get_or_404(Lead, lead_id)
    db.session.delete(lead)
    db.session.commit()
    return jsonify({"message": "deleted"})


@app.route("/leads/stats", methods=["GET"])
def get_stats():
    if not _DATABASE_URL:
        return _db_unavailable()
    statuses = ["New", "Contacted", "Negotiation", "Won", "Lost"]
    data = {"total": Lead.query.count()}
    for s in statuses:
        data[s.lower()] = Lead.query.filter_by(status=s).count()
    return jsonify(data)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
