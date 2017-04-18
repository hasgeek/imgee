# -*- coding: utf-8 -*-

from flask import (render_template, request, url_for, redirect, flash)
from coaster.views import load_models, load_model

from imgee import app, forms, lastuser
from imgee.models import Label, StoredFile, Profile, db


@app.route('/<profile>/<label>')
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (Label, {'name': 'label', 'profile': 'profile'}, 'label'),
    permission=['view', 'siteadmin'])
def show_label(profile, label):
    files = label.stored_files.order_by('stored_file.created_at desc').all()
    form = forms.EditLabelForm()
    return render_template('show_label.html', form=form, label=label, files=files, profile=profile)


@app.route('/<profile>/newlabel', methods=['GET', 'POST'])
@lastuser.requires_login
@load_model(Profile, {'name': 'profile'}, 'profile',
    permission=['new-label', 'siteadmin'])
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
    return render_template('create_label.html', form=form, profile=profile)


@app.route('/<profile>/<label>/delete', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (Label, {'name': 'label', 'profile': 'profile'}, 'label'),
    permission=['delete', 'siteadmin'])
def delete_label(profile, label):
    form = forms.RemoveLabelForm()
    if form.is_submitted():
        utils_delete_label(label)
        flash('The label "%s" was deleted.' % label.name)
        return redirect(url_for('profile_view', profile=profile.name))
    return render_template('delete_label.html', form=form, label=label, profile=profile)


@app.route('/<profile>/<label>/edit', methods=['POST'])
@lastuser.requires_login
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (Label, {'name': 'label', 'profile': 'profile'}, 'label'),
    permission=['edit', 'siteadmin'])
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
    permission=['edit', 'siteadmin'])
def manage_labels(profile, img):
    form = forms.AddLabelForm(stored_file_id=img.id)
    if form.validate_on_submit():
        form_label_data = form.labels.data.strip()
        saved, msg = utils_save_labels(form_label_data, img, profile)
        if msg:
            flash(msg)
        return redirect(url_for('view_image', profile=profile.name, image=img.name))
    return render_template('view_image.html', form=form, img=img)


def utils_save_labels(form_label_data, img, profile):
    msg = ""
    form_lns = set()
    if form_label_data:
        form_lns = set(l.strip() for l in form_label_data.split(','))
    profile_lns = set(l.title for l in profile.labels)
    labels = [l for l in profile.labels if l.title in form_lns]
    for lname in form_lns - profile_lns:
        l = utils_save_label(lname, profile, commit=False)
        labels.append(l)
    s, saved = img.add_labels(labels)
    if saved:
        db.session.commit()
        status = {'+': ('Added', 'to'), '-': ('Removed', 'from'), '': ('Saved', 'to')}
        plural = 's' if len(saved) > 1 else ''
        msg = "%s label%s '%s' %s '%s'." % (status[s][0], plural, "', '".join(l.title for l in saved), status[s][1], img.title)
    return saved, msg


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
