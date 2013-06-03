from imgee import init_for, app
from urlparse import urlparse

init_for('dev')
REDIS_URL = app.config['REDIS_URL']

# REDIS_URL is not taken by setup_default_arguments function of rq/scripts/__init__.py
# so, parse in pieces and give it

r = urlparse(REDIS_URL)
REDIS_HOST = r.hostname
REDIS_PORT = r.port
REDIS_PASSWORD = r.password
REDIS_DB = 0
