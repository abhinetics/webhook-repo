import uuid
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from app.extensions import mongo

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')


@webhook.route('/receiver', methods=["POST"])
def receiver():
    # Get event type from GitHub header
    event_type = request.headers.get("X-GitHub-Event")
    payload = request.get_json()

    if not event_type or not payload:
        return jsonify({"error": "Invalid request"}), 400

    document = None

    # Handle push event
    if event_type == "push":
        ref = payload.get("ref", "")
        # ref usually looks like: refs/heads/main
        to_branch = ref.replace("refs/heads/", "") if ref.startswith("refs/heads/") else ref

        document = {
            "request_id": str(uuid.uuid4()),
            "author": payload.get("pusher", {}).get("name", "unknown"),
            "action": "PUSH",
            "from_branch": "",
            "to_branch": to_branch,
            "timestamp": datetime.now(timezone.utc).strftime("%d %B %Y - %I:%M %p UTC"),
        }

    # Handle pull request events (including merge)
    elif event_type == "pull_request":
        pr = payload.get("pull_request", {})
        merged = pr.get("merged", False)
        action_str = payload.get("action", "")

        # If PR is closed and merged → treat as MERGE
        if action_str == "closed" and merged:
            action = "MERGE"
        else:
            action = "PULL_REQUEST"

        document = {
            "request_id": str(uuid.uuid4()),
            "author": payload.get("sender", {}).get("login", "unknown"),
            "action": action,
            "from_branch": pr.get("head", {}).get("ref", ""),
            "to_branch": pr.get("base", {}).get("ref", ""),
            "timestamp": datetime.now(timezone.utc).strftime("%d %B %Y - %I:%M %p UTC"),
        }

    else:
        # Ignore other GitHub events
        return jsonify({"status": "ignored", "event": event_type}), 200

    # Save event to MongoDB
    mongo.db.events.insert_one(document)

    return jsonify({"status": "ok", "request_id": document["request_id"]}), 200