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
        self.key = 'imgee:registry:%s' % name

    def set_connection(self, connection):
        self.connection = connection

    def add(self, imgname):
        # add with a `score` of `expiry_in_secs` + `now`
        # expiry is set to an hour and can be customized in settings.py
        score = app.config.get('REDIS_KEY_EXPIRY', 3600) + now_in_secs()
        self.connection.zadd(self.key, imgname, score)

    def remove(self, imgname):
        self.connection.zrem(self.key, imgname)

    def remove_expired(self):
        # remove expired keys i.e., keys with score less than now_in_secs
        max_score = now_in_secs()
        self.connection.zremrangebyscore(self.key, 0, max_score)

    def __contains__(self, imgname):
        return bool(self.connection.zrank(self.key, imgname))


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
        if taskid in registry:
            job = AsyncResult(taskid, app=imgee.celery)
            if job.status == celery.states.SUCCESS:
                return job.result
        else:
            # add in the registry and enqueue the job
            registry.add(taskid)
            job = func.apply_async(args=args, kwargs=kwargs, task_id=taskid)

        # remove all the expired jobs
        registry.remove_expired()
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
