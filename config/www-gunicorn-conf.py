bind = "unix:/home/rpetit/staphopia.com/logs/gunicorn-staphopia.sock"

workers = 8
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

loglevel = 'info'
errorlog = '/home/rpetit/staphopia.com/logs/gunicorn_error.log'
accesslog = '/home/rpetit/staphopia.com/logs/gunicorn_access.log'

preload = True
