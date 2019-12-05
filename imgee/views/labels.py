# -*- coding: utf-8 -*-

from flask import abort, flash, redirect, render_template, request, url_for

from flask_babelex import gettext, ngettext

from coaster.views import load_model, load_models
from imgee import app, forms, lastuser
from imgee.models import Label, Profile, StoredFile, db


@app.route('/<profile>/<label>')
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (Label, {'name': 'label', 'profile': 'profile'}, 'label'),
    permission=['view', 'siteadmin'],
    addlperms=lastuser.permissions,
)
def show_label(profile, label):
    files = label.stored_files.order_by(db.desc(StoredFile.created_at)).all()
    form = forms.EditLabelForm()
    return render_template(
        'show_label.html.jinja2', form=form, label=label, files=files, profile=profile
    )


@app.route('/<profile>/newlabel', methods=['GET', 'POST'])
@lastuser.requires_login
@load_model(
    Profile,
    {'name': 'profile'},
    'profile',
    permission=['new-label', 'siteadmin'],
    addlperms=lastuser.permissions,
)
def create_label(profile):
    form = forms.CreateLabelForm(profile_id=profile.id)
    # profile_id is not filled in modal form, fill it here.
    if not form.profile_id.data:
        form.profile_id.data = profile.id
    if form.validate_on_submit():
        label = form.label.data
        utils_save_label(label, profile)
        flash('The label "%s" was created.' % label)
        return redirect(url_for('profile_view', profile=profile.name))
    return render_template('create_label.html.jinja2', form=form, profile=profile)


@app.route('/<profile>/<label>/delete', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (Label, {'name': 'label', 'profile': 'profile'}, 'label'),
    permission=['delete', 'siteadmin'],
    addlperms=lastuser.permissions,
)
def delete_label(profile, label):
    form = forms.RemoveLabelForm()
    if form.is_submitted():
        utils_delete_label(label)
        flash('The label "%s" was deleted.' % label.name)
        return redirect(url_for('profile_view', profile=profile.name))
    return render_template(
        'delete_label.html.jinja2', form=form, label=label, profile=profile
    )


@app.route('/<profile>/<label>/edit', methods=['POST'])
@lastuser.requires_login
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (Label, {'name': 'label', 'profile': 'profile'}, 'label'),
    permission=['edit', 'siteadmin'],
    addlperms=lastuser.permissions,
)
def edit_label(profile, label):
    form = forms.EditLabelForm()
    if form.validate_on_submit():
        label_id = request.form.get('label_id')
        if label.id != int(label_id):
            abort(404)
        label.name = request.form.get('label_name')
        db.session.commit()
        return label.name
    else:
        return form.label_name.errors[0], 400


@app.route('/<profile>/save_labels/<image>', methods=['POST'])
@lastuser.requires_login
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (StoredFile, {'name': 'image', 'profile': 'profile'}, 'img'),
    permission=['edit', 'siteadmin'],
    addlperms=lastuser.permissions,
)
def manage_labels(profile, img):
    form = forms.AddLabelForm(stored_file_id=img.id)
    if form.validate_on_submit():
        form_label_data = form.labels.data.strip()
        total_saved, msg = utils_save_labels(form_label_data, img, profile)
        if msg:
            flash(msg)
        return redirect(url_for('view_image', profile=profile.name, image=img.name))
    return render_template('view_image.html.jinja2', form=form, img=img)


def utils_save_labels(form_label_data, img, profile):
    msg = ""
    total_saved = 0
    form_lns = set()

    if form_label_data:
        form_lns = {l.strip() for l in form_label_data.split(',')}
    profile_lns = {l.title for l in profile.labels}
    labels = [l for l in profile.labels if l.title in form_lns]
    for lname in form_lns - profile_lns:
        label = utils_save_label(lname, profile, commit=False)
        labels.append(label)
    status = img.add_labels(labels)

    if status['+'] or status['-']:
        # if any labels have been added or removed
        db.session.commit()

        for s in ['+', '-']:
            num_saved = len(status[s])

            if num_saved == 0:
                continue

            total_saved += num_saved
            label_names = "', '".join(l.title for l in status[s])
            status_template = {
                '+': ngettext(
                    'Added %(num)s label to', 'Added %(num)s labels to', num_saved
                ),
                '-': ngettext(
                    'Removed %(num)s label from',
                    'Removed %(num)s labels from',
                    num_saved,
                ),
            }
            msg += '{status_text} "{img_name}": "{label_names}". '.format(
                status_text=status_template[s],
                img_name=img.title,
                label_names=label_names,
            )
    else:
        # no new labels were added or removed
        msg = gettext('No new labels were added or removed.')
    return total_saved, msg


def utils_save_label(label_name, profile, commit=True):
    label = Label(title=label_name, profile=profile)
    label.make_name()
    db.session.add(label)
    if commit:
        db.session.commit()
    return label


def utils_delete_label(label):
    if isinstance(label, str):
        label = Label.query.filter_by(title=label).first()
    db.session.delete(label)
    db.session.commit()
