import redis
from imgee import app


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

    def keys_starting_with(self, query):
        return filter(lambda k: k.startswith(query), self.connection.smembers(self.key))

    def search(self, query):
        return filter(lambda k: str(query) in k, self.connection.smembers(self.key))

    def get_all_keys(self):
        return list(self.connection.smembers(self.key))
