import redis
from flask.ext.rq import get_queue

from imgee import app
import storage, utils


def queueit(funcname, *args, **kwargs):
    q = get_queue(kwargs.pop('queue', app.config.get('DEFAULT_QUEUE')))

    if funcname.endswith('save_on_s3'):
        kwargs.setdefault('bucket', utils.get_s3_bucket())
        kwargs.setdefault('folder', utils.get_s3_folder())

    fullpath = lambda fname: 'imgee.storage.%s' % (fname)

    try:
        # if redis is running that can be used by RQ, queue the job
        job = q.enqueue(fullpath(funcname), *args, **kwargs)
    except (redis.exceptions.ConnectionError, TypeError):
        # log the error here and run the function right away.
        return getattr(storage, funcname)(*args, **kwargs)
    else:
        return job

