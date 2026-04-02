#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -eq 0 ]; then
    python3 "$SCRIPT_DIR/pi_startup.py"
else
    node "$SCRIPT_DIR/node_modules/tsx/dist/cli.mjs" "$SCRIPT_DIR/packages/coding-agent/src/cli.ts" "$@"
fi
