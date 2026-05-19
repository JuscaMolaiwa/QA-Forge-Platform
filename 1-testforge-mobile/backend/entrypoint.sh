#!/bin/bash
set -e

ADB_HOST="${ADB_HOST:-}"
ADB_PORT="${ADB_PORT:-5555}"

# If an ADB_HOST is set (Docker emulator container), connect to it over TCP
if [ -n "$ADB_HOST" ]; then
    echo "[entrypoint] Waiting for ADB at ${ADB_HOST}:${ADB_PORT}..."
    for i in $(seq 1 30); do
        if adb connect "${ADB_HOST}:${ADB_PORT}" 2>&1 | grep -q "connected"; then
            echo "[entrypoint] ADB connected to ${ADB_HOST}:${ADB_PORT}"
            adb devices
            break
        fi
        echo "[entrypoint] Attempt $i/30 — retrying in 5s..."
        sleep 5
    done
fi

echo "[entrypoint] Starting Flask backend..."
exec python3 app.py
