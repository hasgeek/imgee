# -*- coding: utf-8 -*-

import os.path
from flask.ext.wtf import (Form, FileField, Required, ValidationError,
            TextField, HiddenField, Length, SelectField, SelectMultipleField)
from imgee.models import Label

def valid_file(form, field):
    filename = field.data.filename
    name, extn = os.path.splitext(filename)
    if not extn:
        raise ValidationError("Sorry, file format unknown. Please try uploading another file.")

class UploadImageForm(Form):
    uploaded_file = FileField("Uploaded File", validators=[Required(), valid_file])

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
    label = SelectMultipleField('Labels', validators=[Required()], coerce=int)
    stored_file_id = HiddenField('stored_file_id')

class RemoveLabelForm(Form):
    pass
