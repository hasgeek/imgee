import redis
from imgee import app


class TaskRegistry(object):
    def __init__(self, name='default', connection=None):
        self.connection = connection or self.set_connection_from_url()
        self.name = name
        self.key_prefix = 'imgee:registry:%s' % name

    def set_connection_from_url(self, url=None):
        url = url or app.config.get('REDIS_URL')
        self.connection = redis.from_url(url)
        return self.connection

    def _key(self, taskid):
        return "{prefix}:{taskid}".format(prefix=self.key_prefix, taskid=taskid)

    def __contains__(self, taskid):
        return len(self.connection.keys(self._key(taskid))) > 0

    def add(self, taskid):
        self.connection.set(self._key(taskid), taskid)
        # setting TTL of 60 seconds for the key
        # if the file doesn't get processed within 60 seconds,
        # it'll be removed from the eregistry
        self.connection.expire(self._key(taskid), 60)

    def remove(self, taskid):
        self.remove_by_key(self._key(taskid))

    def remove_by_key(self, key):
        self.connection.delete(key)

    def search(self, query):
        return filter(lambda k: str(query) in k, self.connection.keys("*" + self._key(query + "*")))

    def get_all_keys(self):
        # >> KEYS imgee:registry:default:*
        return list(self.connection.keys(self._key("*")))

    def keys_starting_with(self, query):
        # >> KEYS imgee:registry:default:query*
        return self.connection.keys(self._key(query + "*"))

    def remove_keys_starting_with(self, query):
        keys = self.keys_starting_with(query)
        for k in keys:
            self.remove_by_key(k)

    def remove_all(self):
        for k in self.get_all_keys():
            self.remove_by_key(k)
