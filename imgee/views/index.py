# -*- coding: utf-8 -*-
import os.path
from werkzeug import secure_filename
from uuid import uuid4
from flask import (render_template, request, g, jsonify, url_for,
                abort, redirect, flash)
from urlparse import urljoin

from imgee import app, forms
from imgee.models import StoredFile, db, Profile, Label
from imgee.views.login import lastuser, authorize, login_required
from imgee.storage import delete_on_s3, save, get_resized_image, get_file_type

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new', methods=('GET', 'POST'))
@authorize
@login_required
def upload_file():
    profileid = g.user.userid
    upload_form = forms.UploadImageForm()
    if upload_form.validate_on_submit():
        filename = secure_filename(request.files['uploaded_file'].filename)
        uniq_name = uuid4().hex
        profile = Profile.query.filter_by(userid=profileid).first()
        stored_file = StoredFile(name=uniq_name, title=filename, profile=profile)
        db.session.add(stored_file)
        db.session.commit()
        content_type = get_file_type(filename)
        save(request.files['uploaded_file'], stored_file.name, content_type=content_type)
        profile_name = Profile.query.filter_by(userid=profileid).one().name
        flash('"%s" uploaded successfully.' % filename)
        return redirect(url_for('show_profile', profile_name=profile_name))
    # form invalid or request.method == 'GET'
    return render_template('form.html', form=upload_form)

@app.route('/<profile_name>')
@login_required
@authorize
def show_profile(profile_name):
    files = StoredFile.query.filter(Profile.name == profile_name).all()
    labels = Label.query.filter(Profile.name == profile_name).all()
    return render_template('profile.html', files=files, labels=labels, profile_name=profile_name)

@app.route('/view/<img_name>')
def view_image(img_name):
    img = StoredFile.query.filter_by(name=img_name).first_or_404()
    labels = [label.name for label in img.labels]
    return render_template('view_image.html', img=img, labels=labels)

@app.route('/file/<img_name>')
def get_image(img_name):
    img = StoredFile.query.filter_by(name=img_name).first_or_404()
    size = request.args.get('size', '')
    img_name = get_resized_image(img, size)
    return redirect(urljoin(app.config.get('MEDIA_DOMAIN'), img_name), code=301)

@app.route('/thumbnail/<img_name>')
def get_thumbnail(img_name):
    img = StoredFile.query.filter_by(name=img_name).first()
    if not img: abort(404)
    tn_size = app.config.get('THUMBNAIL_SIZE')
    thumbnail = get_resized_image(img, tn_size, thumbnail=True)
    return redirect(urljoin(app.config.get('MEDIA_DOMAIN'), thumbnail), code=301)

@app.route('/delete/<img_name>', methods=('GET','POST'))
@login_required
@authorize
def delete_file(img_name):
    stored_file = StoredFile.query.filter_by(name=img_name).first()
    profile_name = Profile.query.filter_by(userid=g.user.userid).one().name
    if stored_file:
        form = forms.DeleteImageForm()
        if form.is_submitted():
            delete_on_s3(stored_file)
            db.session.delete(stored_file)
            db.session.commit()
            flash("%s is deleted" % stored_file.title)
        else:
            return render_template('delete.html', form=form, filename=img_name, profile_name=profile_name)
    else:
        flash("No file found", category="error") # put in appropriate message
    return redirect(url_for('show_profile', profile_name=profile_name))

