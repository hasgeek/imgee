
## Usage: $python runcelery.py `env` -A 'imgee.storage' worker -l info
## `env` could be 'dev' for development or 'prod' for 'production'

import sys
from imgee import init_for, app, celery

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >> sys.stderr, "Usage: {} [env] [celery parameters]".format(sys.argv[0])
        sys.exit(1)
    init_for(sys.argv[1])
    with app.app_context():
        celery.start([sys.argv[0]] + sys.argv[2:])
