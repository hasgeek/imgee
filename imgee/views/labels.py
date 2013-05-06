# -*- coding: utf-8 -*-

from flask import (render_template, request, g, url_for,
                    abort, redirect, flash)
from imgee import app, forms
from imgee.views.login import auth
from imgee.models import Label, StoredFile, Profile
import imgee.utils as utils

def get_profile_label(profile_name, label_name):
    profile = Profile.query.filter(Profile.name==profile_name, Label.name==label_name).first_or_404()
    label = [l for l in profile.labels if l.name == label_name][0]
    return profile, label

@app.route('/<profile_name>/<label_name>')
@auth
def show_label(profile_name, label_name):
    p = Profile.query.filter_by(name=profile_name).first_or_404()
    files = p.stored_files.order_by('created_at desc').all()
    labels = p.labels
    labels.sort(key=lambda x: x.name)
    profile, label = get_profile_label(profile_name, label_name)
    files = label.stored_files.filter(Profile.userid==profile.userid).all()
    return render_template('show_label.html', label=label, files=files, profile_name=g.user.username, labels=labels)

@app.route('/labels/new', methods=('GET', 'POST'))
@auth
def create_label():
    profile_id = g.user.userid
    form = forms.CreateLabelForm(profile_id=profile_id)
    if form.validate_on_submit():
        label = form.label.data
        utils.save_label(label, profile_id)
        flash('The label "%s" was created.' % label)
        return redirect(url_for('show_profile', profile_name=g.user.username))
    return render_template('create_label.html', form=form)

@app.route('/<profile_name>/<label_name>/delete', methods=['GET', 'POST'])
@auth
def delete_label(profile_name, label_name):
    if profile_name != g.user.username:
        abort(403)
    form = forms.RemoveLabelForm()
    profile, label = get_profile_label(profile_name, label_name)
    if form.is_submitted():
        utils.delete_label(label)
        flash('The label "%s" was deleted.' % label_name)
        return redirect(url_for('show_profile', profile_name=profile_name))
    return render_template('delete_label.html', form=form, label=label)

@app.route('/<profile_name>/save_labels/<img_name>', methods=['POST'])
@auth
def manage_labels(profile_name, img_name):
    if profile_name != g.user.username:
        abort(403)
    profile = Profile.query.filter(Profile.name==profile_name, StoredFile.name==img_name).first_or_404()
    stored_file = [s for s in profile.stored_files if s.name == img_name][0]
    image_labels = [l.name for l in stored_file.labels]
    form = forms.AddLabelForm()
    form.label.choices = [(l.id, l.name) for l in profile.labels]
    if form.validate_on_submit():
        labels = [l for l in profile.labels if l.id in form.label.data]
        s, saved = utils.save_labels_to(stored_file, labels)
        if saved:
            status = {'+': ('Added', 'to'), '-': ('Removed', 'from'), '': ('Saved', 'to')}
            plural = 's' if len(saved) > 1 else ''
            flash("%s label%s '%s' %s '%s'." % (status[s][0], plural, "', '".join(l.name for l in saved), status[s][1], stored_file.title))
        return redirect(url_for('view_image', img_name=img_name))
    return render_template('view_image.html', form=form, img=stored_file, labels=image_labels)
