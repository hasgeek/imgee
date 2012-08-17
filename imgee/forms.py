# -*- coding: utf-8 -*-

from flask.ext.wtf import Form, FileField


class UploadForm(Form):
    uploaded_file = FileField("Uploaded File")
