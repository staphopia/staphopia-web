bind = "127.0.0.1:8000"

workers = 8
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

errorlog = '/home/staphopia/staphopia.com/logs/error.log'
loglevel = 'info'
accesslog = '/home/staphopia/staphopia.com/logs/access.log'

preload = True
