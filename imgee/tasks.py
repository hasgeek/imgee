import redis
import time

from imgee import app


def now_in_secs():
    return int(time.time())


def get_taskid(funcname, imgname):
    return "{f}:{n}".format(f=funcname, n=imgname)


class TaskRegistry(object):
    def __init__(self, name='default', connection=None):
        self.connection = redis.from_url(connection) if connection else None
        self.name = name
        self.key = 'imgee:registry:%s' % name

    def set_connection(self, connection=None):
        connection = connection or app.config.get('REDIS_URL')
        self.connection = redis.from_url(connection)

    def add(self, taskid):
        self.connection.sadd(self.key, taskid)

    def remove(self, taskid):
        self.connection.srem(self.key, taskid)

    def remove_all(self):
        for k in self.get_all_keys():
            self.remove(k)

    def __contains__(self, taskid):
        return self.connection.sismember(self.key, taskid)

    def keys_starting_with(self, exp):
        return [k for k in self.connection.smembers(self.key) if k.startswith(exp)]

    def get_all_keys(self):
        return [k for k in self.connection.smembers(self.key)]

    def is_queued_for_deletion(self, imgname):
        taskid = get_taskid('delete', imgname)
        return taskid in self