import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

API_KEY = os.environ.get("API_KEY")
EMAIL = os.environ.get("EMAIL")  # <-- CHANGE THIS to your exam login email


# Add the "yes, other websites may talk to me" headers to EVERY response
@app.after_request
def add_cors_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key"
    resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return resp


@app.route("/analytics", methods=["POST", "OPTIONS"])
def analytics():
    # The browser sends a "preflight" OPTIONS request first, just to ask
    # permission. Answer it quickly, BEFORE checking the key.
    if request.method == "OPTIONS":
        return "", 204

    # 1. Check the API key
    if not API_KEY or request.headers.get("X-API-Key") != API_KEY:
        return jsonify({"error": "unauthorized"}), 401

    # 2. Read the events
    data = request.get_json(silent=True) or {}
    events = data.get("events", [])

    # 3. Do the counting
    total_events = len(events)
    users = set()
    per_user = {}      # user -> total of their POSITIVE amounts
    revenue = 0.0

    for e in events:
        user = e.get("user")
        amount = float(e.get("amount", 0))
        users.add(user)
        if amount > 0:                       # ignore zero and negatives
            revenue += amount
            per_user[user] = per_user.get(user, 0) + amount

    top_user = max(per_user, key=per_user.get) if per_user else None

    # 4. Send the answer
    return jsonify({
        "email": EMAIL,
        "total_events": total_events,
        "unique_users": len(users),
        "revenue": round(revenue, 2),
        "top_user": top_user,
    })
