#!/usr/bin/env bash
# Obsidian Property Studio - local launcher (macOS / Linux)
set -euo pipefail
cd "$(dirname "$0")"
exec python3 -m app "$@"
