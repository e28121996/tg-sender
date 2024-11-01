from threading import Thread

from flask import Flask

app = Flask("")


@app.route("/")
def home() -> str:
    """Health check endpoint untuk UptimeRobot monitoring."""
    return "Bot is running"


def run() -> None:
    """Run Flask server."""

    app.run(host="0.0.0.0", port=8080)  # noqa: S104


def keep_alive() -> None:
    """Start keep-alive server in background thread."""
    t = Thread(target=run)
    t.start()
