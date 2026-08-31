"""Entry point: ``python -m app`` starts the local Property Studio UI."""

from __future__ import annotations

import argparse
import threading
import webbrowser

from .server import APP_VERSION, serve


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m app",
        description="Obsidian Property Studio — local, read-only property governance.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Interface to bind. Defaults to 127.0.0.1 (local only). "
        "Only change this if you understand the exposure.",
    )
    parser.add_argument("--port", type=int, default=8765, help="Port (default 8765).")
    parser.add_argument(
        "--no-browser", action="store_true", help="Do not open a browser automatically."
    )
    parser.add_argument("--version", action="version", version=APP_VERSION)
    args = parser.parse_args()

    if not args.no_browser and args.host in ("127.0.0.1", "localhost"):
        threading.Timer(
            1.0, lambda: webbrowser.open(f"http://localhost:{args.port}")
        ).start()
    serve(args.host, args.port)


if __name__ == "__main__":
    main()
