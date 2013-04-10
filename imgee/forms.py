# -*- coding: utf-8 -*-

import os.path
from flask.ext.wtf import Form, FileField, Required, ValidationError

allowed_extns = 'jpg jpe jpeg png gif bmp'.split()

def valid_image(form, field):
    filename = field.data.filename
    extn = os.path.splitext(filename)[1].lstrip('.')
    if not extn.lower() in allowed_extns:
        raise ValidationError("Sorry, we don't support '%s' images. \
                Please upload images in one of these formats: %s" % (extn, repr(allowed_extns)[1:-1]))

class UploadImageForm(Form):
    uploaded_file = FileField("Uploaded File", validators=[Required(), valid_image])

class DeleteImageForm(Form):
    pass

