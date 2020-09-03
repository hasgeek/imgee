# -*- coding: utf-8 -*-
from flask import abort, flash, jsonify, redirect, render_template, request, url_for

from coaster.auth import current_auth
from coaster.views import load_model, load_models

from .. import app, lastuser
from ..forms import (
    AddLabelForm,
    DeleteImageForm,
    EditTitleForm,
    UpdateTitle,
    UploadImageForm,
)
from ..models import Profile, StoredFile, db
from ..storage import delete, save_file
from ..utils import get_image_url, get_media_domain
from .index import get_prev_next_images


def _redirect_url_frm_upload(profile_name):
    # if the referrer is from 'pop_up_gallery' redirect back to referrer.
    referrer = request.referrer or ''
    if url_for('pop_up_gallery', profile=profile_name) in referrer:
        url = request.referrer
    else:
        url = url_for('profile_view', profile=profile_name)
    return url


@app.route('/<profile>/new', methods=['GET', 'POST'])
@lastuser.requires_login
@load_model(
    Profile,
    {'name': 'profile'},
    'profile',
    permission=['new-file', 'siteadmin'],
    addlperms=lastuser.permissions,
)
def upload_file(profile):
    upload_form = UploadImageForm()
    upload_form.form_nonce.data = upload_form.form_nonce.default()
    if upload_form.validate_on_submit():
        imgfile = request.files['upload_file']
        if imgfile.filename != '':
            title, stored_file = save_file(imgfile, profile=profile)
            flash('"%s" uploaded successfully.' % title)
            return redirect(_redirect_url_frm_upload(profile.name))
    return render_template('form.html.jinja2', form=upload_form, profile=profile)


@app.route('/<profile>/new.json', methods=['POST'])
@lastuser.requires_login
@load_model(
    Profile,
    {'name': 'profile'},
    'profile',
    permission=['new-file', 'siteadmin'],
    addlperms=lastuser.permissions,
)
def upload_file_json(profile):
    upload_form = UploadImageForm()
    if upload_form.validate_on_submit():
        file_ = request.files['upload_file']
        title, stored_file = save_file(file_, profile=profile)
        update_form = UpdateTitle()
        update_form.title.data = stored_file.title
        form = render_template(
            'edit_title_form.html.jinja2',
            form=update_form,
            formid='edit_title_' + stored_file.name,
        )
        return jsonify(
            status=True,
            message="%s uploaded successfully" % title,
            form=form,
            update_url=url_for(
                'update_title_json', profile=profile.name, file=stored_file.name
            ),
            image_data=stored_file.dict_data(),
        )
    else:
        response = jsonify(
            status=False,
            message=' '.join(
                ' '.join(message) for message in upload_form.errors.values()
            ),
        )
        response.status_code = 403
        return response


@app.route('/<profile>/edit_title', methods=['POST'])
@lastuser.requires_login
@load_model(
    Profile,
    {'name': 'profile'},
    'profile',
    permission=['edit', 'siteadmin'],
    addlperms=lastuser.permissions,
)
def edit_title(profile):
    form = EditTitleForm()
    if form.validate_on_submit():
        file_name = request.form.get('file_name')
        if profile.userid not in current_auth.user.user_organizations_adminof_ids():
            abort(403)
        f = StoredFile.query.filter_by(profile=profile, name=file_name).first_or_404()
        f.title = request.form.get('file_title')
        db.session.commit()
        return f.title
    else:
        return form.file_title.errors and form.file_title.errors[0], 400


@app.route('/<profile>/<file>/edit_title.json', methods=['POST'])
@lastuser.requires_login
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (StoredFile, {'name': 'file', 'profile': 'profile'}, 'stored_file'),
    permission=['edit', 'siteadmin'],
    addlperms=lastuser.permissions,
)
def update_title_json(profile, stored_file):
    form = UpdateTitle()
    if form.validate_on_submit():
        old_title = stored_file.title
        form.populate_obj(stored_file)
        db.session.commit()
        return jsonify(
            status=True,
            message="Title for %s has been updated to %s"
            % (old_title, stored_file.title),
            image_data=stored_file.dict_data(),
        )
    else:
        update_form = render_template(
            'edit_title_form.html.jinja2',
            form=form,
            formid='edit_title_' + stored_file.name,
        )
        return jsonify(
            status=False,
            form=update_form,
            update_url=url_for(
                'update_title_json', profile=profile.name, file=stored_file.name
            ),
        )


@app.route('/<profile>/view/<image>')
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (StoredFile, {'name': 'image', 'profile': 'profile'}, 'img'),
    permission=['view', 'siteadmin'],
    addlperms=lastuser.permissions,
)
def view_image(profile, img):
    prev_img, next_img = get_prev_next_images(profile, img)
    form = AddLabelForm(stored_file_id=img.name)
    media_domain = get_media_domain()
    return render_template(
        'view_image.html.jinja2',
        profile=profile,
        form=form,
        img=img,
        prev=prev_img,
        next=next_img,
        domain=media_domain,
    )


@app.route('/embed/file/<image>')
@load_model(StoredFile, {'name': 'image'}, 'image')
def get_image(image):
    size = request.args.get('size')
    image_url = get_image_url(image, size)
    return redirect(image_url, code=301)


@app.route('/<profile>/delete/<image>', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (StoredFile, {'name': 'image', 'profile': 'profile'}, 'img'),
    permission=['delete', 'siteadmin'],
    addlperms=lastuser.permissions,
)
def delete_file(profile, img):
    form = DeleteImageForm()
    if form.validate_on_submit():
        delete(img)
        flash("%s is deleted" % img.title)
    else:
        return render_template(
            'delete.html.jinja2', form=form, file=img, profile=profile
        )
    return redirect(url_for('profile_view', profile=profile.name))
