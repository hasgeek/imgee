# -*- coding: utf-8 -*-

import os.path
from coaster import make_name
from flask_wtf import FlaskForm
from wtforms.validators import Required, ValidationError, Length
from wtforms import (FileField, TextField, HiddenField,
        SelectMultipleField, SelectField)

from imgee import app
from imgee.models import Label
from imgee.utils import get_file_type, is_file_allowed


def valid_file(form, field):
    if not is_file_allowed(field.data.stream, field.data.mimetype, field.data.filename):
        raise ValidationError("Sorry, unknown image format. Please try uploading another file.")


class UploadImageForm(FlaskForm):
    file = FileField("File", validators=[Required(), valid_file])


class DeleteImageForm(FlaskForm):
    pass


class PurgeCacheForm(FlaskForm):
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


class CreateLabelForm(FlaskForm):
    label = TextField('Label', validators=[Required(), Length(max=250), label_doesnt_exist])
    profile_id = HiddenField('profile_id')


class AddLabelForm(FlaskForm):
    stored_file_id = HiddenField('stored_file_id')
    labels = HiddenField('labels')


class RemoveLabelForm(FlaskForm):
    pass


class EditTitleForm(FlaskForm):
    file_name = HiddenField('file_name')
    file_title = TextField('title', validators=[Required(), Length(max=250)])

class UpdateTitle(FlaskForm):
    title = TextField('Title', validators=[Required(), Length(max=250)])


class EditLabelForm(FlaskForm):
    label_name = TextField('label', validators=[Required(), Length(max=250)])


class ChangeProfileForm(FlaskForm):
    profiles = SelectField('Profiles')
