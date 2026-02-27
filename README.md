# Webhook Receiver

Flask app that listens to GitHub webhook events (push, pull request, merge) and stores them in MongoDB. Has a simple UI that shows events in real time.

## Setup

```bash
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/webhookdb?retryWrites=true&w=majority
```

Run it:

```bash
python run.py
```

App runs at `http://127.0.0.1:5000`

## MongoDB Atlas

1. Create a free cluster on [cloud.mongodb.com](https://cloud.mongodb.com)
2. Add a database user (Database Access)
3. Whitelist your IP (Network Access) — use `0.0.0.0/0` for dev
4. Go to Connect → Drivers → Python, copy the URI
5. Paste it in your `.env` file

## Deploy on Render

1. Push code to GitHub
2. Create a new Web Service on [render.com](https://render.com)
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn run:app`
5. Add `MONGO_URI` in Environment Variables

## GitHub Webhook

1. Go to your repo → Settings → Webhooks → Add webhook
2. Payload URL: `https://<your-app-url>/webhook/receiver`
3. Content type: `application/json`
4. Select events: **Pushes** and **Pull requests**
5. Save

Now push code or open/merge PRs — events will show up on the UI.