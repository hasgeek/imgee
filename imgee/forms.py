# -*- coding: utf-8 -*-

from flask.ext.wtf import Form, FileField, Required


class UploadForm(Form):
    uploaded_file = FileField("Uploaded File", validators=[Required()])
