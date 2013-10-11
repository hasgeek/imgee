import redis
from celery import Task
import celery.states
from celery.result import AsyncResult, EagerResult
from flask import url_for, redirect, current_app, make_response
import time

import imgee
from imgee import app
import storage, utils

def now_in_secs():
    return int(time.time())


class TaskRegistry(object):
    def __init__(self, name='default', connection=None):
        self.connection = connection
        self.name = name
        self.prefix = 'imgee:registry:%s' % name

    def set_connection(self, connection):
        self.connection = connection

    def makename(self, funcname, imgname):
        return "{p}:{f}:{n}".format(p=self.prefix, f=funcname, n=imgname)

    def add(self, funcname, imgname):
        # add `imgname` to redis with an expiry of one hour(default)
        # expiry can be customized in settings.py with `REDIS_KEY_EXPIRY`.
        key = self.makename(funcname, imgname)
        expiry = app.config.get('REDIS_KEY_EXPIRY', 3600)
        self.connection.setex(key, 1, expiry)

    def remove(self, imgname):
        key = self.fullname(imgname)
        self.connection.delete(key)

    def __contains__(self, (funcname, imgname)):
        key = self.makename(funcname, imgname)
        return bool(self.connection.exists(key))


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
    else:
        if not registry.connection:
            registry.set_connection(redis.from_url(app.config.get('REDIS_URL')))
        # check it in the registry.
        if (funcname, taskid) in registry:
            job = AsyncResult(taskid, app=imgee.celery)
            if job.status == celery.states.SUCCESS:
                return job.result
        else:
            # add in the registry and enqueue the job
            registry.add(funcname, taskid)
            job = func.apply_async(args=args, kwargs=kwargs, task_id=taskid)
        return job


def loading():
    loading_img_path = app.config.get('LOADING_IMG')
    with open(loading_img_path) as loading_img:
        response = make_response(loading_img.read())
        response.headers['Content-Type'] = utils.get_file_type(loading_img_path)
        return response


def get_async_result(job):
    """
    If the result of the `job` is not yet ready, return that else return loading().
    If the input is `str` instead, return that.
    """
    if isinstance(job, AsyncResult):
        if job.status == celery.states.SUCCESS:
            return job.result
        else:
            return loading()
    elif isinstance(job, (str, unicode)):
        return job
