# -*- coding: utf-8 -*-

import os.path
from flask.ext.wtf import (Form, FileField, Required, ValidationError,
            TextField, HiddenField, Length, SelectField)
from imgee.models import Label

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

def label_doesnt_exist(form, field):
    profile_id = form.profile_id.data
    label_name = field.data
    exists = Label.query.filter_by(profile_id=profile_id, name=label_name).first()
    if exists:
        raise ValidationError('Label "%s" already exists. Please try another name.' % field.data)

class CreateLabelForm(Form):
    label = TextField('Label', validators=[Required(), Length(max=50), label_doesnt_exist])
    profile_id = HiddenField('profile_id')

class AddLabelForm(Form):
    label = SelectField('Label', validators=[Required()])
    profile_id = HiddenField('profile_id')

class RemoveLabelForm(Form):
    pass
