from flask import Blueprint, jsonify, request
from app.extensions import mongo

webhook = Blueprint("webhook", __name__, url_prefix="/webhook")


@webhook.route("/receiver", methods=["POST"])
def receiver():
    event_type = request.headers.get("X-GitHub-Event")
    payload = request.get_json()

    if not event_type or not payload:
        return jsonify({"error": "Invalid request"}), 400

    document = None

    # ---------------- PUSH EVENT ----------------
    if event_type == "push":
        ref = payload.get("ref", "")
        to_branch = ref.replace("refs/heads/", "") if ref.startswith("refs/heads/") else ref

        document = {
            "request_id": payload.get("after", ""),  # commit hash
            "author": payload.get("pusher", {}).get("name", "unknown"),
            "action": "PUSH",
            "from_branch": "",
            "to_branch": to_branch,
            "timestamp": payload.get("head_commit", {}).get("timestamp", ""),
        }

    # ---------------- PULL REQUEST / MERGE ----------------
    elif event_type == "pull_request":
        pr = payload.get("pull_request", {})
        action_name = payload.get("action")

        is_merged = action_name == "closed" and pr.get("merged", False)

        if is_merged:
            action = "MERGE"
            timestamp = pr.get("merged_at", "")
        else:
            action = "PULL_REQUEST"
            timestamp = pr.get("created_at", "")

        document = {
            "request_id": str(pr.get("id", "")),  # PR ID
            "author": pr.get("user", {}).get("login", "unknown"),
            "action": action,
            "from_branch": pr.get("head", {}).get("ref", ""),
            "to_branch": pr.get("base", {}).get("ref", ""),
            "timestamp": timestamp,
        }

    else:
        # Ignore unrelated GitHub events
        return jsonify({"status": "ignored"}), 200

    mongo.db.events.insert_one(document)

    return jsonify({"status": "success"}), 200