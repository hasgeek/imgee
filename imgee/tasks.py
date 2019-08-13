import re
import redis


class InvalidRedisQueryException(Exception):
    pass


class TaskRegistry(object):
    def __init__(self, app=None, name='default', connection=None):
        self.name = name
        self.connection = connection
        self.key_prefix = 'imgee:registry:%s' % name
        self.filename_pattern = re.compile(r'^[a-z0-9_\.]+$')

        if app:
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        self.app = app

        if not self.connection:
            url = self.app.config.get('REDIS_URL')
            self.connection = redis.from_url(url)
            self.pipe = self.connection.pipeline()

    def is_valid_query(self, query):
        return bool(self.filename_pattern.match(query))

    def key_for(self, taskid):
        return u'{key_prefix}:{taskid}'.format(
            key_prefix=self.key_prefix, taskid=taskid
        )

    def __contains__(self, taskid):
        return len(self.connection.keys(self.key_for(taskid))) > 0

    def add(self, taskid, expire=60):
        self.connection.set(self.key_for(taskid), taskid)
        # setting TTL of 60 seconds for the key
        # if the file doesn't get processed within 60 seconds,
        # it'll be removed from the registry
        self.connection.expire(self.key_for(taskid), expire)

    def search(self, query):
        # >> KEYS imgee:registry:default:*query*
        if not self.is_valid_query(query):
            raise InvalidRedisQueryException(
                u'Invalid query for searching redis keys: {}'.format(query)
            )
        return self.connection.keys(self.key_for('*{}*'.format(query)))

    def get_all_keys(self):
        # >> KEYS imgee:registry:default:*
        return self.connection.keys(self.key_for('*'))

    def keys_starting_with(self, query):
        # >> KEYS imgee:registry:default:query_*
        # chances are that we'll use this function to find the
        # thumbnail keys, which look like "name_wNN_hNN", hence the _
        if not self.is_valid_query(query):
            raise InvalidRedisQueryException(
                u'Invalid query for searching redis keys, starting with: {}'.format(
                    query
                )
            )
        return self.connection.keys(self.key_for('{}_*'.format(query)))

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
        # query will most likely be stored_file.name, So
        # Delete keys for only `<query>` and `<query>_*`
        self.remove_keys([self.key_for(query)] + self.keys_starting_with(query))

    def remove_all(self):
        self.remove_keys(self.get_all_keys())
