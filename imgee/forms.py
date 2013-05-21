# -*- coding: utf-8 -*-

import os.path
from coaster import make_name
from flask.ext.wtf import (Form, FileField, Required, ValidationError,
    TextField, HiddenField, Length, SelectMultipleField, SelectField)

from imgee import app
from imgee.models import Label


allowed_formats = 'jpg jpe jpeg png gif bmp tiff psd tif eps svg ai ps'.split()


def valid_file(form, field):
    filename = field.data.filename
    name, extn = os.path.splitext(filename)
    if not extn or extn.strip('.') not in allowed_formats:
        raise ValidationError("Sorry, unknown image format. Please try uploading another file.")


class UploadImageForm(Form):
    uploaded_file = FileField("Uploaded File", validators=[Required(), valid_file])


class DeleteImageForm(Form):
    pass


def reserved_words():
    """get all words which can't be used as labels"""
    words = []
    for rule in app.url_map.iter_rules():
        r = rule.rule
        if r.startswith('/<profile>/'):
            words.append(r.replace('/<profile>/', '').split('/', 1)[0])
    return words


def label_doesnt_exist(form, field):
    profile_id = form.profile_id.data
    label_name = make_name(field.data)
    if label_name in reserved_words():
        raise ValidationError('"%s" is reserved and cannot be used as a label. Please try another name.' % label_name)

    exists = Label.query.filter_by(profile_id=profile_id, name=label_name).first()
    if exists:
        raise ValidationError('Label "%s" already exists. Please try another name.' % field.data)


class CreateLabelForm(Form):
    label = TextField('Label', validators=[Required(), Length(max=250), label_doesnt_exist])
    profile_id = HiddenField('profile_id')


class AddLabelForm(Form):
    stored_file_id = HiddenField('stored_file_id')
    labels = HiddenField('labels')


class RemoveLabelForm(Form):
    pass


class EditTitleForm(Form):
    file_name = HiddenField('file_name')
    file_title = TextField('title', validators=[Required(), Length(max=250)])


class EditLabelForm(Form):
    label_name = TextField('label', validators=[Required(), Length(max=250)])


class ChangeProfileForm(Form):
    profiles = SelectField('Profiles')
