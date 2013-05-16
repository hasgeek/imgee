# -*- coding: utf-8 -*-
import os.path
from werkzeug import secure_filename
from uuid import uuid4
from flask import (render_template, request, g, url_for,
    redirect, flash)
from urlparse import urljoin
from sqlalchemy import and_, not_

from coaster.views import load_model, load_models
from imgee import app, forms, lastuser
from imgee.models import StoredFile, db, Profile
from imgee.storage import delete_on_s3, save, get_resized_image, get_file_type, get_s3_folder
from imgee.utils import newid

image_formats = 'jpg jpe jpeg png gif bmp'.split()


@app.route('/')
def index():
    return render_template('index.html')


def _get_owned_ids(user=None):
    user = user or g.user
    if user is not None:
        return user.user_organizations_owned_ids()


def _redirect_url_frm_upload(profile_name):
    # if the referrer is from 'pop_up_gallery' redirect back to referrer.
    referrer = request.referrer or ''
    if url_for('pop_up_gallery', profile=g.user.profile_name) in referrer:
        url = request.referrer
    else:
        url = url_for('profile_view', profile=profile_name)
    return url


@app.route('/<profile>/new', methods=['GET', 'POST'])
@load_model(Profile, {'name': 'profile'}, 'profile',
    permission=['new-file', 'siteadmin'], addlperms=lastuser.permissions)
def upload_file(profile):
    profileid = g.user.userid
    upload_form = forms.UploadImageForm()
    if upload_form.validate_on_submit():
        filename = secure_filename(request.files['uploaded_file'].filename)
        stored_file = StoredFile(name=newid(), title=filename, profile=profile)
        db.session.add(stored_file)
        db.session.commit()
        content_type = get_file_type(filename)
        save(request.files['uploaded_file'], stored_file.name, content_type=content_type)
        profile_name = Profile.query.filter_by(userid=profileid).one().name
        flash('"%s" uploaded successfully.' % filename)
        return redirect(_redirect_url_frm_upload(profile_name))
    # form invalid or request.method == 'GET'
    return render_template('form.html', form=upload_form)


@app.route('/<profile>/popup')
@load_model(Profile, {'name': 'profile'}, 'profile',
    permission=['view', 'siteadmin'], addlperms=lastuser.permissions)
def pop_up_gallery(profile):
    files = profile.stored_files.order_by('created_at desc').all()
    form = forms.UploadImageForm()
    cp_form = forms.ChangeProfileForm()
    cp_form.profiles.choices = [(p.id, p.name) for p in g.user.profiles]
    return render_template('pop_up_gallery.html', files=files, profile_name=profile.name,
            uploadform=form, cp_form=cp_form)


@app.route('/<profile>/edit_title', methods=['POST'])
@load_model(Profile, {'name': 'profile'}, 'profile',
    permission=['edit', 'siteadmin'], addlperms=lastuser.permissions)
def edit_title(profile):
    form = forms.EditTitleForm()
    if form.validate_on_submit():
        file_name = request.form.get('file_name')
        q = and_(Profile.userid.in_(_get_owned_ids()), StoredFile.name == file_name)
        f = StoredFile.query.filter(q).first_or_404()
        f.title = request.form.get('file_title')
        db.session.commit()
        return f.title
    else:
        return form.file_title.errors[0], 400


@app.route('/<profile>')
@load_model(Profile, {'name': 'profile'}, 'profile',
    permission=['view', 'siteadmin'], addlperms=lastuser.permissions)
def profile_view(profile):
    files = profile.stored_files.order_by('created_at desc').all()
    form = forms.EditTitleForm()
    return render_template('profile.html', profile=profile, files=files, form=form)

@app.route('/<profile>/archive')
@load_model(Profile, {'name': 'profile'}, 'profile',
    permission=['view', 'siteadmin'], addlperms=lastuser.permissions)
def unlabelled_images(profile):
    """Get all unlabelled images owned by profile"""
    files = profile.stored_files.filter(not_(StoredFile.labels.any())).order_by('created_at desc').all()
    form = forms.EditTitleForm()
    return render_template('profile.html', profile=profile, files=files, form=form, unlabelled=True)


@app.route('/<profile>/view/<img_name>')
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (StoredFile, {'name': 'img_name', 'profile': 'profile'}, 'img'),
    permission=['view', 'siteadmin'], addlperms=lastuser.permissions)
def view_image(profile, img):
    img_labels = [label.name for label in img.labels]
    form = forms.AddLabelForm(img_name=img.name, label=[l.id for l in img.labels])
    form.label.choices = [(l.id, l.name) for l in img.profile.labels]
    return render_template('view_image.html', form=form, img=img, labels=img_labels)


@app.route('/file/<img_name>')
def get_image(img_name):
    img = StoredFile.query.filter_by(name=img_name).first_or_404()
    name, extn = os.path.splitext(img.title)
    if extn and extn.lstrip('.').lower() in image_formats:
        size = request.args.get('size', '')
        img_name = get_resized_image(img, size)
    img_name = get_s3_folder() + img_name + extn
    return redirect(urljoin(app.config.get('MEDIA_DOMAIN'), img_name), code=301)


@app.route('/<profile>/thumbnail/<img_name>')
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (StoredFile, {'name': 'img_name', 'profile': 'profile'}, 'img'),
    permission=['view', 'siteadmin'], addlperms=lastuser.permissions)
def get_thumbnail(profile, img):
    name, extn = os.path.splitext(img.title)
    if extn and extn.lstrip('.').lower() in image_formats:
        tn_size = app.config.get('THUMBNAIL_SIZE')
        thumbnail = get_resized_image(img, tn_size, thumbnail=True)
        thumbnail = get_s3_folder() + thumbnail + extn
    else:
        thumbnail = app.config.get('UNKNOWN_FILE_THUMBNAIL')
    return redirect(urljoin(app.config.get('MEDIA_DOMAIN'), thumbnail), code=301)


@app.route('/<profile>/delete/<img_name>', methods=['GET', 'POST'])
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (StoredFile, {'name': 'img_name', 'profile': 'profile'}, 'img'),
    permission=['delete', 'siteadmin'], addlperms=lastuser.permissions)
def delete_file(profile, img):
    form = forms.DeleteImageForm()
    if form.is_submitted():
        delete_on_s3(img)
        db.session.delete(img)
        db.session.commit()
        flash("%s is deleted" % img.title)
    else:
        return render_template('delete.html', form=form, file=img, profile=profile)
    return redirect(url_for('profile_view', profile=profile.name))
