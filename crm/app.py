import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, Lead

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "CRITICAL: DATABASE_URL is not set. "
        "Production CRM requires PostgreSQL."
    )

# Render provides postgres:// URIs; SQLAlchemy 1.4+ requires postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print("[STARTUP] DATABASE_URL detected:", bool(DATABASE_URL))

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    print("[STARTUP] Connected to PostgreSQL — tables verified.")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "database": "postgresql",
        "persistent": True,
    })


@app.route("/leads", methods=["GET"])
def get_leads():
    status = request.args.get("status")
    query = Lead.query.order_by(Lead.created_at.desc())
    if status:
        query = query.filter_by(status=status)
    return jsonify([lead.to_dict() for lead in query.all()])


@app.route("/leads", methods=["POST"])
def create_lead():
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
    lead = db.get_or_404(Lead, lead_id)
    db.session.delete(lead)
    db.session.commit()
    return jsonify({"message": "deleted"})


@app.route("/leads/stats", methods=["GET"])
def get_stats():
    statuses = ["New", "Contacted", "Negotiation", "Won", "Lost"]
    data = {"total": Lead.query.count()}
    for s in statuses:
        data[s.lower()] = Lead.query.filter_by(status=s).count()
    return jsonify(data)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
