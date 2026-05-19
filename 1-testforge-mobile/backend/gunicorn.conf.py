import os

# Gevent worker required for Flask-SocketIO
worker_class = "geventwebsocket.gunicorn.workers.GeventWebSocketWorker"
workers = 1  # must be 1 for SocketIO shared state
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
timeout = 120
keepalive = 5
