# gunicorn.conf.py
workers = 2
worker_class = 'sync'
bind = '127.0.0.1:5000'
preload_app = True
timeout = 30
