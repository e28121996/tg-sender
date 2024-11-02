"""Web server untuk keep-alive."""

from threading import Thread
from typing import Final

from flask import Flask

from .logger import setup_logger

# Setup logger
logger = setup_logger(name=__name__)

# Konstanta
HOST: Final[str] = "127.0.0.1"
PORT: Final[int] = 8080

# Setup Flask dengan logging minimal
app = Flask(__name__)


@app.route("/")
def home() -> str:
    """Health check endpoint."""
    return "Bot is running"


def run() -> None:
    """Run Flask server dengan error handling."""
    try:
        # Disable Flask internal logging
        app.logger.disabled = True

        app.run(
            host=HOST,
            port=PORT,
            debug=False,  # Disable debug mode
            use_reloader=False,  # Disable reloader
        )
    except Exception as e:
        # Log error tapi jangan crash program utama
        logger.error("❌ Error pada web server: %s", str(e))


def start_server() -> None:
    """Start web server untuk keep-alive."""
    try:
        server_thread: Thread = Thread(target=run, daemon=True)
        server_thread.start()
        logger.info("✅ Web server started on %s:%d", HOST, PORT)
    except Exception as e:
        error_msg: str = str(e)
        logger.error("❌ Error saat start web server: %s", error_msg)


# Expose fungsi yang akan digunakan
keep_alive = start_server

__all__ = ["keep_alive"]
