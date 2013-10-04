import redis
import celery.states
from celery.result import AsyncResult, EagerResult

from imgee import app, imgeecelery
import storage, utils


class TaskRegistry(object):
    def __init__(self, name='default', connection=None):
        # @@ TODO: take redis url from app.config
        self.connection = connection or redis.from_url("redis://localhost:6379/0")
        self.name = name
        self.key = 'rq:registry:%s' % name

    def add(self, imgname):
        self.connection.sadd(self.key, imgname)

    def remove(self, imgname):
        self.connection.delete(self.key, imgname)

    def __contains__(self, imgname):
        return self.connection.sismember(self.key, imgname)



# @@ TODO: find a better place to init TaskRegistry
registry = TaskRegistry()


def queueit(funcname, *args, **kwargs):
    """
    Execute `funcname` function with `args` and `kwargs` if CELERY_ALWAYS_EAGER is True.
    Otherwise, check if it's queued already in `TaskRegistry`. If not, add it to `TaskRegistry` and queue it.
    """
    func = getattr(storage, funcname)
    taskid = kwargs.pop('taskid')
    if app.config.get('CELERY_ALWAYS_EAGER'):
        return func(*args, **kwargs)
        # return func.apply(*args, **kwargs).get()
    else:
        # check it in the registry.
        if taskid in registry:
            job = AsyncResult(taskid, app=imgeecelery)
            if job.status == celery.states.SUCCESS:
                return job.result
        else:
            # add in the registry and enqueue the job
            registry.add(taskid)
            job = func.apply_async(args=args, kwargs=kwargs, task_id=taskid)
        return job

