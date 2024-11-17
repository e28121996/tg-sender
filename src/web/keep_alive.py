"""Modul untuk menjaga bot tetap berjalan dengan web server Flask."""

from threading import Event, Thread

from flask import Flask


class WebServer:
    """Pengelola web server Flask."""

    def __init__(self) -> None:
        """Inisialisasi web server."""
        self.app = Flask(__name__)
        self.shutdown_event = Event()
        self.server_thread: Thread | None = None

        # Setup routes
        self.app.route("/")(self.home)

    @staticmethod
    def home() -> str:
        """Route handler untuk homepage."""
        return "Bot sedang berjalan!"

    def run(self) -> None:
        """Menjalankan Flask server pada host dan port yang ditentukan."""
        self.app.run(host="0.0.0.0", port=8080)

    def start(self) -> None:
        """Memulai web server dalam thread terpisah."""
        self.server_thread = Thread(target=self.run)
        self.server_thread.daemon = True
        self.server_thread.start()

    def shutdown(self) -> None:
        """Menghentikan web server dengan aman."""
        if self.server_thread and self.server_thread.is_alive():
            self.shutdown_event.set()
            self.server_thread.join(timeout=1)
            self.server_thread = None


# Singleton instance
server = WebServer()
keep_alive = server.start
shutdown_server = server.shutdown
