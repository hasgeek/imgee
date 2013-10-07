
## Usage: $python runcelery.py `env` -A 'imgee.storage' worker -l info
## for production env, use '--prod' for `env` above.

import sys
from imgee import init_for, app, celery

if __name__ == '__main__':
    if sys.argv and sys.argv[1] == '--prod':
        init_for('prod')
    else:
        init_for('dev')
    
    with app.app_context():
        celery.start()
