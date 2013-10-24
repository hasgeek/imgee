# -*- coding: utf-8 -*-
import os.path
from flask import (render_template, request, g, url_for,
    redirect, flash, Response)
from sqlalchemy import and_, not_

from coaster.views import load_model, load_models
from imgee import app, forms, lastuser
from imgee.models import StoredFile, db, Profile
from imgee.storage import delete, save, clean_local_cache
from imgee.utils import newid, get_media_domain, not_in_deleteQ
from imgee.async import queueit
import imgee.async as async
import imgee.utils as utils


@app.context_processor
def global_vars():
    cl_form = forms.CreateLabelForm()
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
        title, job = save(file_, profile=profile)
        flash('"%s" uploaded successfully.' % title)
        return redirect(_redirect_url_frm_upload(profile.name))
    return render_template('form.html', form=upload_form, profile=profile)


@app.route('/<profile>/popup')
@load_model(Profile, {'name': 'profile'}, 'profile',
    permission=['view', 'siteadmin'], addlperms=lastuser.permissions)
def pop_up_gallery(profile):
    files = profile.stored_files.order_by('created_at desc').all()
    files = not_in_deleteQ(files)
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
        return form.file_title.errors and form.file_title.errors[0], 400


@app.route('/<profile>')
@load_model(Profile, {'name': 'profile'}, 'profile')
def profile_view(profile):
    files = profile.stored_files.order_by('created_at desc').all()
    files = not_in_deleteQ(files)
    title_form = forms.EditTitleForm()
    upload_form = forms.UploadImageForm()
    return render_template('profile.html', profile=profile, files=files, uploadform=upload_form, title_form=title_form)


@app.route('/<profile>/archive')
@load_model(Profile, {'name': 'profile'}, 'profile',
    permission=['view', 'siteadmin'], addlperms=lastuser.permissions)
def unlabelled_images(profile):
    """Get all unlabelled images owned by profile"""
    files = profile.stored_files.filter(not_(StoredFile.labels.any())).order_by('created_at desc').all()
    files = not_in_deleteQ(files)
    title_form = forms.EditTitleForm()
    return render_template('profile.html', profile=profile, files=files, title_form=title_form, unlabelled=True)

def get_prev_next_images(profile, img, limit=2):
    # query for "all" images though we need just the `limit`
    # bcoz we don't know how many are there in deleteQ.
    imgs = profile.stored_files.order_by('created_at desc').all()
    imgs = not_in_deleteQ(imgs)
    pos = imgs.index(img)
    return imgs[pos+1 : pos+1+limit], imgs[pos-limit : pos]

@app.route('/<profile>/view/<image>')
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (StoredFile, {'name': 'image', 'profile': 'profile'}, 'img'),
    permission=['view', 'siteadmin'], addlperms=lastuser.permissions)
def view_image(profile, img):
    prev, next = get_prev_next_images(profile, img)
    form = forms.AddLabelForm(stored_file_id=img.name)
    media_domain = get_media_domain()
    return render_template('view_image.html', profile=profile, form=form, img=img,
                    prev=prev, next=next, domain=media_domain)


@app.route('/embed/file/<image>')
@load_model(StoredFile, {'name': 'image'}, 'image')
def get_image(image):
    size = request.args.get('size')
    try:
        image_url = utils.get_image_url(image, size)
    except async.StillProcessingException:
        return async.loading()
    else:
        return redirect(image_url, code=301)


@app.route('/embed/thumbnail/<image>')
@load_model(StoredFile, {'name': 'image'}, 'image')
def get_thumbnail(image):
    try:
        tn_url = utils.get_thumbnail_url(image, size)
    except async.StillProcessingException:
        return async.loading()
    else:
        return redirect(tn_url, code=301)


@app.route('/<profile>/delete/<image>', methods=['GET', 'POST'])
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (StoredFile, {'name': 'image', 'profile': 'profile'}, 'img'),
    permission=['delete', 'siteadmin'], addlperms=lastuser.permissions)
def delete_file(profile, img):
    form = forms.DeleteImageForm()
    if form.is_submitted():
        queueit('delete', img, taskid=img.name + img.extn)
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
