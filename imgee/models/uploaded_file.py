# -*- coding: utf-8 -*-

from coaster.sqlalchemy import BaseNameMixin
from imgee.models import db


class UploadedFile(BaseNameMixin, db.Model):
    __tablename__ = 'file'
