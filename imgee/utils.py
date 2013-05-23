# -*- coding: utf-8 -*-

from uuid import uuid4
from flask import request

from retask.queue import Queue
from retask.task import Task

from imgee import app

def newid():
    return unicode(uuid4().hex)

def get_media_domain():
    scheme = request.scheme
    return '%s:%s' % (scheme, app.config.get('MEDIA_DOMAIN'))

class ImageQueue(Queue):
    def __init__(self, qname='retask_queue'):
        config = dict(host=app.config.get('REDIS_HOST', 'localhost'),
                    port=app.config.get('REDIS_PORT', 6379),
                    password=app.config.get('REDIS_PASSWORD', None),
                    db=app.config.get('REDIS_DB', 0))
        super(ImageQueue, self).__init__(qname, config)

    def add(self, image_name):
        image = Task(dict(name=image_name))
        self.connect()
        self.enqueue(image)
