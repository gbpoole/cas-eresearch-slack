from multiprocessing import cpu_count

# Socket Path
bind = 'unix:/var/www/app/cas-eresearch-slack/gunicorn.sock'

# Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
loglevel  = 'debug'
accesslog = '/var/www/app/cas-eresearch-slack/access_log'
errorlog  = '/var/www/app/cas-eresearch-slack/error_log'
