# -*- coding: utf-8 -*-

from flask import (render_template, request, g, url_for,
                    abort, redirect, flash)
from imgee import app, forms
from imgee.views.login import authorize, login_required
from imgee.models import Label, StoredFile, Profile
import imgee.utils as utils

def get_profile_label(profile_name, label_name):
    p = Profile.query.filter(Profile.name==profile_name, Label.name==label_name).first_or_404()
    return p, p.labels[0]

@app.route('/<profile_name>/<label_name>')
@login_required
@authorize
def show_label(profile_name, label_name):
    profile, label = get_profile_label(profile_name, label_name)
    files = label.files.filter(Profile.userid==profile.userid).all()
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

@app.route('/<profile_name>/<label_name>/delete', methods=('POST'))
@login_required
@authorize
def delete_label(profile_name, label_name):
    if profile_name != g.user.username:
        abort(403)
    profile, label = get_profile_label(profile_name, label_name)
    utils.delete_label(label)
    flash('The label "%s" was deleted.' % label_name)
    return redirect(url_for('show_profile', profile_name=profile_name))

@app.route('/<profile_name>/add/<img_name>', methods=('GET', 'POST'))
def add_label_to(label_name, img_name):
    pass

@app.route('/<profile_name>/del/<img_name>', methods=('GET', 'POST'))
def remove_label_from(img_name):
    pass

