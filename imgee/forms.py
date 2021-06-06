from baseframe import forms
from coaster.utils import make_name

from . import app
from .models import Label
from .utils import is_file_allowed


def valid_file(form, field):
    if not is_file_allowed(field.data.stream, field.data.mimetype, field.data.filename):
        raise forms.ValidationError(
            "Sorry, unknown image format. Please try uploading another file."
        )


class UploadImageForm(forms.Form):
    upload_file = forms.FileField(
        "File", validators=[forms.validators.DataRequired(), valid_file]
    )


class DeleteImageForm(forms.Form):
    pass


class PurgeCacheForm(forms.Form):
    pass


def reserved_words():
    """Get all words which can't be used as labels"""
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
        raise forms.ValidationError(
            "“%s” is reserved and cannot be used as a label. Please try another name."
            % label_name
        )

    exists = Label.query.filter_by(profile_id=profile_id, name=label_name).first()
    if exists:
        raise forms.ValidationError(
            "Label “%s” already exists. Please try another name." % field.data
        )


class CreateLabelForm(forms.Form):
    label = forms.StringField(
        'Label',
        validators=[
            forms.validators.DataRequired(),
            forms.validators.Length(max=250),
            label_doesnt_exist,
        ],
    )
    profile_id = forms.HiddenField('profile_id')


class AddLabelForm(forms.Form):
    stored_file_id = forms.HiddenField('stored_file_id')
    labels = forms.HiddenField('labels')


class RemoveLabelForm(forms.Form):
    pass


class EditTitleForm(forms.Form):
    file_name = forms.HiddenField('file_name')
    file_title = forms.StringField(
        'title',
        validators=[forms.validators.DataRequired(), forms.validators.Length(max=250)],
    )


class UpdateTitle(forms.Form):
    title = forms.StringField(
        'Title',
        validators=[forms.validators.DataRequired(), forms.validators.Length(max=250)],
    )


class EditLabelForm(forms.Form):
    label_name = forms.StringField(
        'label',
        validators=[forms.validators.DataRequired(), forms.validators.Length(max=250)],
    )


class ChangeProfileForm(forms.Form):
    profiles = forms.SelectField('Profiles')
