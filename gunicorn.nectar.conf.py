# Gunicorn configuration for Nectar deployment

# Non logging stuff
bind = "0.0.0.0:8080"
workers = 4
worker_class = 'uvicorn.workers.UvicornWorker'

# Access log - records incoming HTTP requests
accesslog = "/home/ubuntu/gunicorn.access.log"

# Error log - records Gunicorn server goings-on
errorlog = "/home/ubuntu/gunicorn.error.log"

# Whether to send application output to the error log 
capture_output = True

# How verbose the Gunicorn error logs should be 
loglevel = "info"
