# settings for the RQ worker
# usage: rqworker -c rqconfig


from urlparse import urlparse
from imgee import init_for, app

init_for('production')
REDIS_URL = app.config.get('REDIS_URL', 'redis://localhost:6379/0')

r = urlparse(REDIS_URL)
REDIS_HOST = r.hostname
REDIS_PORT = r.port
REDIS_PASSWORD = r.password
REDIS_DB = 0

QUEUES = ['high', 'default']

