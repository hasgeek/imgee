# -*- coding: utf-8 -*-

from flask import (render_template, request, g, url_for,
    redirect, flash)
from coaster.views import load_models, load_model

from imgee import app, forms, lastuser
from imgee.models import Label, StoredFile, Profile, db


@app.route('/<profile>/<label>')
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (Label, {'name': 'label', 'profile': 'profile'}, 'label'),
    permission=['view', 'siteadmin'], addlperms=lastuser.permissions)
def show_label(profile, label):
    files = label.stored_files.order_by('stored_file.created_at desc').all()
    form = forms.EditLabelForm()
    return render_template('show_label.html', form=form, label=label, files=files, profile=profile)


@app.route('/<profile>/newlabel', methods=['GET', 'POST'])
@load_model(Profile, {'name': 'profile'}, 'profile',
    permission=['new-label', 'siteadmin'], addlperms=lastuser.permissions)
def create_label(profile):
    profile_id = g.user.userid
    form = forms.CreateLabelForm(profile_id=profile_id)
    if form.validate_on_submit():
        label = form.label.data
        utils_save_label(label, profile)
        flash('The label "%s" was created.' % label)
        return redirect(g.user.profile_url)
    return render_template('create_label.html', form=form, profile=profile)


@app.route('/<profile>/<label>/delete', methods=['GET', 'POST'])
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (Label, {'name': 'label_name', 'profile': 'profile'}, 'label'),
    permission=['delete', 'siteadmin'], addlperms=lastuser.permissions)
def delete_label(profile, label):
    form = forms.RemoveLabelForm()
    if form.is_submitted():
        utils_delete_label(label)
        flash('The label "%s" was deleted.' % label.name)
        return redirect(url_for('profile_view', profile=profile.name))
    return render_template('delete_label.html', form=form, label=label)


@app.route('/<profile>/<label>/edit', methods=['POST'])
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (Label, {'name': 'label', 'profile': 'profile'}, 'label'),
    permission=['edit', 'siteadmin'], addlperms=lastuser.permissions)
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
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (StoredFile, {'name': 'image', 'profile': 'profile'}, 'img'),
    permission=['edit', 'siteadmin'], addlperms=lastuser.permissions)
def manage_labels(profile, img):
    form = forms.AddLabelForm(stored_file_id=img.id)
    form.label.choices = [(l.id, l.title) for l in profile.labels]
    if form.validate_on_submit():
        if not form.hlabels.data.strip():
            form_lns = set()
        else:
            form_lns = set(l.strip() for l in form.hlabels.data.split(','))
        profile_lns = set(l.title for l in profile.labels)
        labels = [l for l in profile.labels if l.title in form_lns]
        for lname in form_lns - profile_lns:
            l = utils_save_label(lname, profile, commit=False)
            labels.append(l)
        s, saved = utils_save_labels_to(img, labels)
        if saved:
            status = {'+': ('Added', 'to'), '-': ('Removed', 'from'), '': ('Saved', 'to')}
            plural = 's' if len(saved) > 1 else ''
            flash("%s label%s '%s' %s '%s'." % (status[s][0], plural, "', '".join(l.title for l in saved), status[s][1], img.title))
        return redirect(url_for('view_image', profile=g.user.profile_name, image=img.name))
    return render_template('view_image.html', form=form, img=img)


def utils_save_label(label_name, profile, commit=True):
    label = Label(title=label_name, profile=profile)
    label.make_name()
    db.session.add(label)
    if commit:
        db.session.commit()
    return label


def utils_delete_label(label):
    db.session.delete(label)
    db.session.commit()


def utils_get_label_changes(nlabels, olabels):
    if (nlabels == olabels):
        status, diff = '0', []
    elif (nlabels > olabels):
        status, diff = '+', nlabels-olabels
    elif (olabels > nlabels):
        status, diff = '-', olabels-nlabels
    else:
        status, diff = '', nlabels
    return status, list(diff)


def utils_save_labels_to(stored_file, labels):
    new_labels = set(labels)
    old_labels = set(stored_file.labels)
    if new_labels != old_labels:
        stored_file.labels = labels
        db.session.commit()
    return utils_get_label_changes(new_labels, old_labels)
