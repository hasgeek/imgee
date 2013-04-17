# -*- coding: utf-8 -*-

from flask import (render_template, request, g, url_for,
                    abort, redirect, flash)
from imgee import app, forms
from imgee.views.login import authorize, login_required
from imgee.models import Label, StoredFile, Profile
import imgee.utils as utils

def get_profile_label(profile_name, label_name):
    profile = Profile.query.filter(Profile.name==profile_name, Label.name==label_name).first_or_404()
    label = [l for l in profile.labels if l.name == label_name][0]
    return profile, label

@app.route('/<profile_name>/<label_name>')
@login_required
@authorize
def show_label(profile_name, label_name):
    profile, label = get_profile_label(profile_name, label_name)
    files = label.stored_files.filter(Profile.userid==profile.userid).all()
    return render_template('show_label.html', label=label.name, files=files)

@app.route('/labels/new', methods=('GET', 'POST'))
@login_required
@authorize
def create_label():
    profile_id = g.user.userid
    form = forms.CreateLabelForm(profile_id=profile_id)
    if form.validate_on_submit():
        label = form.label.data
        utils.save_label(label, profile_id)
        flash('The label "%s" was created.' % label)
        return redirect(url_for('show_profile', profile_name=g.user.username))
    return render_template('create_label.html', form=form)

@app.route('/<profile_name>/<label_name>/delete', methods=['POST'])
@login_required
@authorize
def delete_label(profile_name, label_name):
    if profile_name != g.user.username:
        abort(403)
    profile, label = get_profile_label(profile_name, label_name)
    utils.delete_label(label)
    flash('The label "%s" was deleted.' % label_name)
    return redirect(url_for('show_profile', profile_name=profile_name))

@app.route('/<profile_name>/add_label/<img_name>', methods=['POST'])
@login_required
@authorize
def add_label_to(profile_name, img_name):
    if profile_name != g.user.username:
        abort(403)
    profile = Profile.query.filter(Profile.name==profile_name, StoredFile.name==img_name).first_or_404()
    stored_file = [s for s in profile.stored_files if s.name == img_name][0]
    image_labels = [l.name for l in stored_file.labels]
    form = forms.AddLabelForm()
    form.label.choices = [(l.id, l.name) for l in profile.labels]
    if form.validate_on_submit():
        label_id = form.label.data
        label = [l for l in profile.labels if l.id == label_id][0]
        if utils.save_label_to(stored_file, label):
            flash('Added label "%s" to "%s".' % (label.name, stored_file.title))
        return redirect(url_for('view_image', img_name=img_name, profile_name=profile_name))
    return render_template('view_image.html', form=form, img=stored_file, labels=image_labels)

@app.route('/<profile_name>/del_label/<img_name>', methods=['POST'])
def remove_label_from(img_name):
    if profile_name != g.user.username:
        abort(403)
    profile = Profile.query.filter(Profile.name==profile_name, StoredFile.name==img_name).first_or_404()
    stored_file = [s for s in profile.stored_files if s.name == img_name][0]
    form = forms.RemoveLabelForm()

    if form.validate_on_submit():
        label_id = form.label.data
        label = [l for l in profile.labels if l.id == label_id][0]
        if utils.remove_label_from(stored_file, label):
            flash('Removed label "%s" from "%s".' % (label.name, stored_file.title))
        return redirect(url_for('view_image', img_name=img_name, profile_name=profile_name))
    return render_template('view_image.html', form=form, img=stored_file, labels=image_labels)
