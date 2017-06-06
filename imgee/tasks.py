import re
import redis
from imgee import app


class TaskRegistry(object):
    def __init__(self, name='default', connection=None):
        self.connection = connection or self.set_connection_from_url()
        self.name = name
        self.key_prefix = 'imgee:registry:%s' % name
        self.filename_pattern = '^[a-z0-9\_\.]+$'
        self.pipe = self.connection.pipeline()

    def set_connection_from_url(self, url=None):
        url = url or app.config.get('REDIS_URL')
        self.connection = redis.from_url(url)
        return self.connection

    def key_for(self, taskid):
        return u'{key_prefix}:{taskid}'.format(key_prefix=self.key_prefix, taskid=taskid)

    def __contains__(self, taskid):
        return len(self.connection.keys(self.key_for(taskid))) > 0

    def add(self, taskid, expire=60):
        self.connection.set(self.key_for(taskid), taskid)
        # setting TTL of 60 seconds for the key
        # if the file doesn't get processed within 60 seconds,
        # it'll be removed from the eregistry
        self.connection.expire(self.key_for(taskid), expire)

    def search(self, query):
        # >> KEYS imgee:registry:default:*query*
        if not re.compile(self.filename_pattern).match(query):
            return list()
        return self.connection.keys(self.key_for('*{}*'.format(query)))

    def get_all_keys(self):
        # >> KEYS imgee:registry:default:*
        return self.connection.keys(self.key_for('*'))

    def keys_starting_with(self, query):
        # >> KEYS imgee:registry:default:query*
        if not re.compile(self.filename_pattern).match(query):
            return list()
        return self.connection.keys(self.key_for('{}*'.format(query)))

    def remove(self, taskid):
        # remove a key with the taskid
        self.remove_by_key(self.key_for(taskid))

    def remove_by_key(self, key):
        # remove a redis key directly
        self.connection.delete(key)

    def remove_keys(self, keys):
        for k in keys:
            self.pipe.delete(k)
        self.pipe.execute()

    def remove_keys_matching(self, query):
        self.remove_keys(self.search(query))

    def remove_keys_starting_with(self, query):
        self.remove_keys(self.keys_starting_with(query))

    def remove_all(self):
        self.remove_keys(self.get_all_keys())
