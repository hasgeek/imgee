# -*- coding: utf-8 -*-

from flask.ext.wtf import Form, FileField


def UploadForm(Form):
    uploaded_file = FileField("Uploaded File")
