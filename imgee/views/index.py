# -*- coding: utf-8 -*-
import os.path
from werkzeug import secure_filename
from flask import (render_template, request, g, url_for,
    redirect, flash, Response)
from urlparse import urljoin
from sqlalchemy import and_, not_

from coaster.views import load_model, load_models
from imgee import app, forms, lastuser
from imgee.models import StoredFile, db, Profile
from imgee.storage import delete_on_s3, save, get_resized_image, clean_local_cache
from imgee.utils import newid, get_media_domain, get_s3_folder
from imgee.async import get_async_result

image_formats = '.jpg .jpe .jpeg .png .gif .bmp'.split()


@app.context_processor
def global_vars():
    profile_id = g.user and (g.user.profile and g.user.profile.id) or None
    cl_form = forms.CreateLabelForm(profile_id=profile_id)
    return {'cl_form': cl_form, 'uf_form': forms.UploadImageForm()}


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
    if url_for('pop_up_gallery', profile=profile_name) in referrer:
        url = request.referrer
    else:
        url = url_for('profile_view', profile=profile_name)
    return url


@app.route('/<profile>/new', methods=['GET', 'POST'])
@load_model(Profile, {'name': 'profile'}, 'profile',
    permission=['new-file', 'siteadmin'], addlperms=lastuser.permissions)
def upload_file(profile):
    upload_form = forms.UploadImageForm()
    if upload_form.validate_on_submit():
        file_ = request.files['file']
        filename = secure_filename(file_.filename)
        save(file_, profile=profile)
        flash('"%s" uploaded successfully.' % filename)
        return redirect(_redirect_url_frm_upload(profile.name))
    # form invalid or request.method == 'GET'
    return render_template('form.html', form=upload_form, profile=profile)


@app.route('/<profile>/popup')
@load_model(Profile, {'name': 'profile'}, 'profile',
    permission=['view', 'siteadmin'], addlperms=lastuser.permissions)
def pop_up_gallery(profile):
    files = profile.stored_files.order_by('created_at desc').all()
    form = forms.UploadImageForm()
    cp_form = forms.ChangeProfileForm()
    cp_form.profiles.choices = [(p.id, p.name) for p in g.user.profiles]
    return render_template('pop_up_gallery.html', files=files, profile=profile, uploadform=form, cp_form=cp_form)


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
@load_model(Profile, {'name': 'profile'}, 'profile')
def profile_view(profile):
    files = profile.stored_files.order_by('created_at desc').all()
    title_form = forms.EditTitleForm()
    upload_form = forms.UploadImageForm()
    return render_template('profile.html', profile=profile, files=files, uploadform=upload_form, title_form=title_form)


@app.route('/<profile>/archive')
@load_model(Profile, {'name': 'profile'}, 'profile',
    permission=['view', 'siteadmin'], addlperms=lastuser.permissions)
def unlabelled_images(profile):
    """Get all unlabelled images owned by profile"""
    files = profile.stored_files.filter(not_(StoredFile.labels.any())).order_by('created_at desc').all()
    title_form = forms.EditTitleForm()
    return render_template('profile.html', profile=profile, files=files, title_form=title_form, unlabelled=True)


def get_prev_images(profile, img, limit=2):
    imgs = profile.stored_files.filter(StoredFile.created_at < img.created_at)
    return imgs.order_by('created_at desc').limit(limit).all()[::1]


def get_next_images(profile, img, limit=2):
    imgs = profile.stored_files.filter(StoredFile.created_at > img.created_at)
    return imgs.order_by('created_at asc').limit(limit).all()[::-1]


@app.route('/<profile>/view/<image>')
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (StoredFile, {'name': 'image', 'profile': 'profile'}, 'img'),
    permission=['view', 'siteadmin'], addlperms=lastuser.permissions)
def view_image(profile, img):
    prev = get_prev_images(profile, img)
    next = get_next_images(profile, img)
    form = forms.AddLabelForm(stored_file_id=img.name)
    media_domain = get_media_domain()
    return render_template('view_image.html', profile=profile, form=form, img=img,
                    prev=prev, next=next, domain=media_domain)


@app.route('/embed/file/<image>')
@load_model(StoredFile, {'name': 'image'}, 'image')
def get_image(image):
    extn = image.extn
    if extn in image_formats:
        size = request.args.get('size', '')
        if not size:
            img_name = image.name
        else:
            img_name = get_async_result(get_resized_image(image, size))
            if isinstance(img_name, Response):
                return img_name
    else:
        img_name = image.name
    img_name = get_s3_folder() + img_name + extn
    media_domain = get_media_domain()
    return redirect(urljoin(media_domain, img_name), code=301)


@app.route('/embed/thumbnail/<image>')
@load_model(StoredFile, {'name': 'image'}, 'image')
def get_thumbnail(image):
    extn = image.extn
    if extn in image_formats:
        tn_size = app.config.get('THUMBNAIL_SIZE')
        thumbnail = get_async_result(get_resized_image(image, tn_size, is_thumbnail=True))
        if isinstance(thumbnail, Response):
            return thumbnail
        thumbnail = get_s3_folder() + thumbnail + extn
    else:
        thumbnail = app.config.get('UNKNOWN_FILE_THUMBNAIL')
    media_domain = get_media_domain()
    return redirect(urljoin(media_domain, thumbnail), code=301)


@app.route('/<profile>/delete/<image>', methods=['GET', 'POST'])
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (StoredFile, {'name': 'image', 'profile': 'profile'}, 'img'),
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


@app.route('/_admin/purge-cache', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
def purge_cache():
    form = forms.PurgeCacheForm()
    if form.is_submitted():
        removed = clean_local_cache(app.config.get('CACHE_PURGE_PERIOD', 24))
        flash('%s files are deleted from the cache.' % removed)
    return render_template('purge_cache.html', form=form)
