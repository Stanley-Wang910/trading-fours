# gunicorn.conf.py
workers = 2
worker_class = 'sync'
bind = '0.0.0.0:5000'
preload_app = True
timeout = 120
# accesslog
accesslog = '-'
errorlog = '-'
capture_output = True
threads = 3
