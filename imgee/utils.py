# -*- coding: utf-8 -*-

from uuid import uuid4


def newid():
    return unicode(uuid4().hex)
