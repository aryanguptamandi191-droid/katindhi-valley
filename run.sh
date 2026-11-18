#!/usr/bin/env bash
# Quick start script for Katindhi Valley General Store Wholesale Web Application
cd "$(dirname "$0")"
PORT="${1:-8080}"
echo "Starting Katindhi Valley General Store Web Server on port ${PORT}..."
python3 server.py "${PORT}"
