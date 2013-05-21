# -*- coding: utf-8 -*-

from uuid import uuid4
from flask import request
from imgee import app

def newid():
    return unicode(uuid4().hex)

def get_media_domain():
    scheme = request.scheme
    return '%s:%s' % (scheme, app.config.get('MEDIA_DOMAIN'))
