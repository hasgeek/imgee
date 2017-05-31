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

    def _make_key(self, taskid):
        return "{key_prefix}:{taskid}".format(key_prefix=self.key_prefix, taskid=taskid)

    def __contains__(self, taskid):
        return len(self.connection.keys(self._make_key(taskid))) > 0

    def add(self, taskid, expire=60):
        self.connection.set(self._make_key(taskid), taskid)
        # setting TTL of 60 seconds for the key
        # if the file doesn't get processed within 60 seconds,
        # it'll be removed from the eregistry
        self.connection.expire(self._make_key(taskid), expire)

    def search(self, query):
        # >> KEYS imgee:registry:default:*query*
        return self.connection.keys(self._make_key("*{}*".format(query)))

    def get_all_keys(self):
        # >> KEYS imgee:registry:default:*
        return self.connection.keys(self._make_key("*"))

    def keys_starting_with(self, query):
        # >> KEYS imgee:registry:default:query*
        return self.connection.keys(self._make_key("{}*".format(query)))

    def remove(self, taskid):
        # remove a key with the taskid
        self.remove_by_key(self._make_key(taskid))

    def remove_by_key(self, key):
        # remove a redis key directly
        self.connection.delete(key)

    def remove_keys_matching(self, query):
        keys = self.search(query)
        for k in keys:
            self.remove_by_key(k)

    def remove_keys_starting_with(self, query):
        keys = self.keys_starting_with(query)
        for k in keys:
            self.remove_by_key(k)

    def remove_all(self):
        for k in self.get_all_keys():
            self.remove_by_key(k)
