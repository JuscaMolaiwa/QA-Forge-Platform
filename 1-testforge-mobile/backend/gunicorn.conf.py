import os

# Threading worker — no C extensions needed, works on any Python version
worker_class = "gthread"
workers = 1        # must be 1 for SocketIO shared state
threads = 4
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
timeout = 120
keepalive = 5