bind = "127.0.0.1:8000"

workers = 8
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

loglevel = 'info'
errorlog = '/staphopia/ebs/staphopia.com/logs/gunicorn_error.log'
accesslog = '/staphopia/ebs/staphopia.com/logs/gunicorn_access.log'

preload = True
