#!/usr/bin/env bash
cd "$(dirname "$0")"
PORT="${PORT:-8080}"
python server.py "${PORT}" || python3 server.py "${PORT}"
