import os

from flask import Flask, jsonify, render_template
from flask_cors import CORS

from app.extensions import mongo
from app.webhook.routes import webhook


def create_app():
    # my Flask app
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates'),
        static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static'),
    )

    # MongoDB config (uses env variable in production, local fallback for dev)
    app.config["MONGO_URI"] = os.environ.get(
        "MONGO_URI", "mongodb://localhost:27017/webhookdb"
    )
    CORS(app)

    # Initialize Mongo extension
    mongo.init_app(app)

    # Register webhook blueprint
    app.register_blueprint(webhook)

    # Home route to serve UI
    @app.route("/")
    def index():
        return render_template("index.html")

    # API to fetch stored events (latest fetched first)
    @app.route("/events")
    def events():
        cursor = mongo.db.events.find({}, {"_id": 0}).sort("_id", -1)
        return jsonify(list(cursor)), 200

    return app