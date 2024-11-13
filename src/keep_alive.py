"""Web server untuk keep-alive di Replit."""

from threading import Thread
from typing import Any, Final

from flask import Flask
from werkzeug.serving import WSGIRequestHandler

from .logger import setup_logger

logger = setup_logger(name=__name__)

# Konstanta
HOST: Final[str] = "0.0.0.0"
PORT: Final[int] = 8080

app = Flask(__name__)


class CustomWSGIRequestHandler(WSGIRequestHandler):
    """Custom WSGI request handler that disables request logging."""

    def log_request(self, *args: Any, **kwargs: Any) -> None:
        """Override log_request to disable request logging.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        pass


# Use custom handler
app.config["REQUEST_HANDLER"] = CustomWSGIRequestHandler


@app.route("/")
def home() -> str:
    """Health check endpoint."""
    return "Bot is running"


def run() -> None:
    """Run Flask server untuk Replit."""
    try:
        # Disable all Flask logging
        app.logger.disabled = True
        import logging

        log = logging.getLogger("werkzeug")
        log.disabled = True

        app.run(host=HOST, port=PORT, debug=False, use_reloader=False)
    except Exception:
        logger.exception("❌ Error pada web server")
        raise


def start_server() -> None:
    """Start web server untuk keep-alive di Replit."""
    try:
        server_thread = Thread(target=run, daemon=True)
        server_thread.start()
        logger.info("✅ Web server started on port %d", PORT)
    except Exception:
        logger.exception("❌ Error saat start web server")
        raise


keep_alive = start_server
