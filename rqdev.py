from imgee import init_for, app
init_for('dev')
REDIS_URL = app.config['REDIS_URL']
