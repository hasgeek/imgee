# -*- coding: utf-8 -*-

from flask import (render_template, request, g, url_for,
                     abort, redirect, flash)
from coaster.views import load_model, load_models

from imgee import app, forms, lastuser
from imgee.models import Label, StoredFile, Profile, db
import imgee.utils as utils


@app.route('/<profile_name>/<label_name>')
@load_models(
    (Profile, {'name': 'profile_name'}, 'profile'),
    (Label, {'name': 'label_name', 'profile': 'profile'}, 'label'),
    permission=['view', 'siteadmin'], addlperms=lastuser.permissions)
def show_label(profile, label):
    files = profile.imgs.order_by('created_at desc').all()
    labels = profile.labels
    labels.sort(key=lambda x: x.name)
    files = label.imgs.filter(Profile.userid == profile.userid).all()
    form = forms.EditLabelForm()
    return render_template('show_label.html', form=form, label=label, files=files, profile_name=g.user.username, labels=labels)

@app.route('/labels/new', methods=('GET', 'POST'))
@lastuser.requires_login
def create_label():
    profile_id = g.user.userid
    form = forms.CreateLabelForm(profile_id=profile_id)
    if form.validate_on_submit():
        label = form.label.data
        utils.save_label(label, profile_id)
        flash('The label "%s" was created.' % label)
        return redirect(url_for('show_profile', profile=g.user.username))
    return render_template('create_label.html', form=form)

@app.route('/<profile_name>/<label_name>/delete', methods=['GET', 'POST'])
@load_models(
    (Profile, {'name': 'profile_name'}, 'profile'),
    (Label, {'name': 'label_name', 'profile': 'profile'}, 'label'),
    permission=['delete', 'siteadmin'], addlperms=lastuser.permissions)
def delete_label(profile, label):
    form = forms.RemoveLabelForm()
    if form.is_submitted():
        utils.delete_label(label)
        flash('The label "%s" was deleted.' % label_name)
        return redirect(url_for('show_profile', profile=profile.name))
    return render_template('delete_label.html', form=form, label=label)

@app.route('/<profile_name>/edit_label', methods=['POST'])
@lastuser.requires_login
def edit_label(profile_name):
    form = forms.EditLabelForm()
    if form.validate_on_submit():
        label_id = request.form.get('label_id')
        label = Label.query.filter(Profile.userid == g.user.userid, Label.id == label_id).first_or_404()
        label.name = request.form.get('label')
        db.session.commit()
        return label.name
    else:
        return form.label.errors[0], 400


@app.route('/<profile_name>/save_labels/<img_name>', methods=['POST'])
@load_models(
    (Profile, {'name': 'profile_name'}, 'profile'),
    (StoredFile, {'name': 'img_name', 'profile': 'profile'}, 'img'),
    permission=['edit', 'siteadmin'], addlperms=lastuser.permissions)
def manage_labels(profile, img):
    form = forms.AddLabelForm()
    form.label.choices = [(l.id, l.name) for l in profile.labels]
    if form.validate_on_submit():
        labels = [l for l in profile.labels if l.id in form.label.data]
        s, saved = utils.save_labels_to(img, labels)
        if saved:
            status = {'+': ('Added', 'to'), '-': ('Removed', 'from'), '': ('Saved', 'to')}
            plural = 's' if len(saved) > 1 else ''
            flash("%s label%s '%s' %s '%s'." % (status[s][0], plural, "', '".join(l.name for l in saved), status[s][1], img.title))
        return redirect(url_for('view_image', profile=g.user.username, img_name=img.name))
    return render_template('view_image.html', form=form, img=img)
