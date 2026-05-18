# Appium Device Farm

A mobile test orchestration platform for Appium-based device execution across local and cloud environments.

## Features

- **Device Pool Management** — auto-discovers Android devices via ADB; supports manual registration for iOS/cloud
- **Test Queue** — thread-safe FIFO queue dispatches tests to available devices
- **Live Dashboard** — WebSocket-powered real-time device status and session progress
- **Concurrent Execution** — multiple Appium servers, one per active device
- **Reports** — pass/fail trends, session history, per-run log output
- **Docker Ready** — full stack containerised with `docker-compose`

## Architecture

```
frontend (React) ──HTTP/WS──► backend (Flask + SocketIO)
                                    │
                         ┌──────────┴──────────┐
                    DeviceManager          TestExecutor
                    (ADB sync)           (pytest runner)
                         │                    │
                      SQLite             QueueManager
                         │                    │
                    Device models        Appium servers
```

## Quick Start

### Option 1 — Docker (recommended)

```bash
cp .env.example .env
docker-compose up --build
```

Frontend → http://localhost:3000  
Backend API → http://localhost:5000/api/health

### Option 2 — Local dev

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r ../requirements.txt
cp ../.env.example .env
python app.py
```

**Frontend**
```bash
cd frontend
npm install
npm start
```

**Appium** (required for real execution)
```bash
npm install -g appium
appium driver install uiautomator2   # Android
appium driver install xcuitest       # iOS
```

## API Reference

See `tests/sample_tests/api/sample_apis.json` for full request/response examples.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check + queue depth |
| GET | `/api/devices/` | List all devices |
| POST | `/api/devices/` | Register a device |
| POST | `/api/devices/sync` | Sync ADB devices |
| DELETE | `/api/devices/{id}` | Remove a device |
| POST | `/api/tests/` | Submit a test session |
| GET | `/api/tests/` | List sessions (filterable by status) |
| GET | `/api/tests/{session_id}` | Get session detail + logs |
| DELETE | `/api/tests/{session_id}` | Cancel a queued session |
| GET | `/api/reports/summary` | Aggregate pass/fail counts |
| GET | `/api/reports/history` | Recent completed sessions |
| GET | `/api/reports/trends` | Daily pass/fail trends |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `development` | Flask environment |
| `SECRET_KEY` | — | Flask secret (change in prod) |
| `APPIUM_HOST` | `localhost` | Appium server host |
| `APPIUM_BASE_PORT` | `4723` | First Appium port |
| `APPIUM_MAX_SESSIONS` | `5` | Max concurrent sessions |
| `SESSION_TIMEOUT_SECONDS` | `300` | Test execution timeout |
| `ADB_PATH` | `adb` | Path to adb binary |
| `DATABASE_URL` | `sqlite:///device_farm.db` | SQLAlchemy DB URL |
| `FRONTEND_URL` | `http://localhost:3000` | CORS allowed origin |

## Writing Tests

Tests are standard `pytest` files using the Appium Python client.  
The executor injects these environment variables automatically:

| Variable | Value |
|----------|-------|
| `APPIUM_HOST` | Appium server host |
| `APPIUM_PORT` | Allocated port for this session |
| `DEVICE_UDID` | Target device UDID |
| `PLATFORM_NAME` | `android` or `ios` |
| `PLATFORM_VERSION` | OS version string |
| `APP_PATH` | Path to the app under test |

See `tests/sample_tests/` for working examples.

## Tech Stack

- **Backend**: Python 3.11, Flask 3, Flask-SocketIO, SQLAlchemy, eventlet
- **Frontend**: React 18, Recharts, Socket.IO client
- **Testing**: Appium Python Client, pytest
- **Infra**: Docker, Docker Compose, ADB (Android Debug Bridge)
