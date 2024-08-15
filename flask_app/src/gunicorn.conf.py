# gunicorn.conf.py
workers = 2
worker_class = 'sync'
bind = '0.0.0.0:5000' # Shouldn't this be local?
preload_app = True
timeout = 30
# accesslog
accesslog = '-'
errorlog = '-'
capture_output = True
max_requests = 500
threads = 3
