# -*- coding: utf-8 -*-
from sqlalchemy import not_

from flask import flash, redirect, render_template, request

from coaster.auth import current_auth
from coaster.views import load_model

from .. import app, forms, lastuser
from ..models import Label, Profile, StoredFile, db
from ..storage import clean_local_cache
from ..utils import ALLOWED_MIMETYPES


@app.context_processor
def global_vars():
    cl_form = forms.CreateLabelForm()
    return {'cl_form': cl_form, 'uf_form': forms.UploadImageForm()}


@app.route('/')
def index():
    return render_template('index.html.jinja2')


@app.route('/account')
@lastuser.requires_login
def account():
    lastuser.update_user(current_auth.user)
    Profile.update_from_user(
        current_auth.user, db.session, make_user_profiles=True, make_org_profiles=True
    )
    db.session.commit()
    return redirect(current_auth.user.profile_url)


@app.route('/<profile>/popup')
@lastuser.requires_login
@load_model(
    Profile,
    {'name': 'profile'},
    'profile',
    permission=['view', 'siteadmin'],
    addlperms=lastuser.permissions,
)
def pop_up_gallery(profile):
    label = request.args.get('label')
    files = profile.stored_files
    if label:
        files = files.join(StoredFile.labels).filter(Label.name == label)
    files = files.order_by(db.desc(StoredFile.created_at)).all()
    form = forms.UploadImageForm()
    cp_form = forms.ChangeProfileForm()
    cp_form.profiles.choices = [(p.id, p.name) for p in current_auth.user.profiles]
    return (
        render_template(
            'pop_up_gallery.html.jinja2',
            files=files,
            label=label,
            profile=profile,
            uploadform=form,
            cp_form=cp_form,
        ),
        200,
        {'X-Frame-Options': 'ALLOW'}
    )


@app.route('/<profile>')
@load_model(Profile, {'name': 'profile'}, 'profile')
def profile_view(profile):
    files = profile.stored_files.order_by(db.desc(StoredFile.created_at)).all()
    title_form = forms.EditTitleForm()
    upload_form = forms.UploadImageForm()
    return render_template(
        'profile.html.jinja2',
        profile=profile,
        files=files,
        uploadform=upload_form,
        title_form=title_form,
        mimetypes=ALLOWED_MIMETYPES.keys(),
    )


@app.route('/<profile>/archive')
@load_model(
    Profile,
    {'name': 'profile'},
    'profile',
    permission=['view', 'siteadmin'],
    addlperms=lastuser.permissions,
)
def unlabelled_images(profile):
    """Get all unlabelled images owned by profile"""
    files = (
        profile.stored_files.filter(not_(StoredFile.labels.any()))
        .order_by(StoredFile.created_at.desc())
        .all()
    )
    title_form = forms.EditTitleForm()
    return render_template(
        'profile.html.jinja2',
        profile=profile,
        files=files,
        title_form=title_form,
        unlabelled=True,
    )


def get_prev_next_images(profile, img, limit=2):
    # query for "all" images though we need just the `limit`
    # bcoz we don't know how many are there in deleteQ.
    prev_img = (
        profile.stored_files.filter(
            StoredFile.created_at <= img.created_at, StoredFile.id != img.id
        )
        .order_by(db.desc(StoredFile.created_at))
        .limit(limit)
        .all()
    )
    next_img = (
        profile.stored_files.filter(
            StoredFile.created_at >= img.created_at, StoredFile.id != img.id
        )
        .order_by(db.asc(StoredFile.created_at))
        .limit(limit)
        .all()
    )
    return prev_img, next_img


@app.route('/_admin/purge-cache', methods=['GET', 'POST'])
@lastuser.requires_login
@lastuser.requires_permission('siteadmin')
def purge_cache():
    form = forms.PurgeCacheForm()
    if form.is_submitted():
        removed = clean_local_cache(app.config.get('CACHE_PURGE_PERIOD', 24))
        flash('%s files are deleted from the cache.' % removed)
    return render_template('purge_cache.html.jinja2', form=form)
