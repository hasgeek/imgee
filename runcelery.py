
## Usage: $python runcelery.py `env` -A 'imgee.storage' worker -l info
## `env` could be '--dev' (default) or '--prod'

import sys
from imgee import init_for, app, celery

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--prod':
        init_for('prod')
    else:
        init_for('dev')

    with app.app_context():
        celery.start()
