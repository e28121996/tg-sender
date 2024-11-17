"""Modul untuk menjaga bot tetap berjalan dengan web server Flask."""

from threading import Thread

from flask import Flask

app = Flask(__name__)


@app.route("/")
def home() -> str:
    """Route handler untuk homepage.

    Returns:
        str: Pesan status bot
    """
    return "Bot sedang berjalan!"


def run() -> None:
    """Menjalankan Flask server pada host dan port yang ditentukan."""
    app.run(host="0.0.0.0", port=8080)


def keep_alive() -> None:
    """Memulai web server dalam thread terpisah."""
    t = Thread(target=run)
    t.start()
