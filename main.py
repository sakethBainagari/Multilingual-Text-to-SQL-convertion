"""
Slim entry-point for the NL-to-SQL application.
All logic lives in the `backend` package; this file only boots the server.
"""

import os
import sys
import signal
from dotenv import load_dotenv

load_dotenv()

from backend import create_app  # noqa: E402

# --- Configuration from environment ---
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("FLASK_ENV", "production") == "development"
DB_PATH = os.getenv("DB_PATH")  # None → use default sample DB

app = create_app(db_path=DB_PATH)


def _graceful_shutdown(sig, frame):
    print(f"\n[INFO] Received signal {sig}, shutting down…")
    sys.exit(0)


signal.signal(signal.SIGINT, _graceful_shutdown)
signal.signal(signal.SIGTERM, _graceful_shutdown)

if __name__ == "__main__":
    print(f"[INFO] Starting NL-to-SQL on http://localhost:{PORT}")
    print(f"[INFO] Debug={DEBUG}  DB={DB_PATH or 'default sample'}")
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
