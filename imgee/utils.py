# -*- coding: utf-8 -*-

from uuid import uuid4
from flask import request
from imgee import app
import mimetypes

def newid():
    return unicode(uuid4().hex)

def get_media_domain():
    scheme = request.scheme
    return '%s:%s' % (scheme, app.config.get('MEDIA_DOMAIN'))

def guess_extension(mimetype):
    if mimetype in ('image/jpg', 'image/jpe', 'image/jpeg'):
        return '.jpeg'    # guess_extension returns .jpe, which PIL doesn't like
    return mimetypes.guess_extension(mimetype)
