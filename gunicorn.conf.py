# Gunicorn configuration file
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "provokely"

# Server mechanics
daemon = False
pidfile = "/var/run/gunicorn/provokely.pid"
user = "ubuntu"
group = "ubuntu"
tmp_upload_dir = None

# SSL (will be configured later with Let's Encrypt)
# keyfile = "/etc/ssl/private/provokely.key"
# certfile = "/etc/ssl/certs/provokely.crt"
