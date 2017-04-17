# -*- coding: utf-8 -*-
from flask import (flash, g, jsonify, redirect, render_template, request, url_for)
from sqlalchemy import and_

from coaster.views import load_model, load_models
from imgee import app, forms, lastuser
from imgee.models import StoredFile, db, Profile
from imgee.storage import delete, save_file
from imgee.utils import get_media_domain
from .index import get_prev_next_images
import imgee.utils as utils


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
@load_model(Profile, {'name': 'profile'}, 'profile',
    permission=['new-file', 'siteadmin'])
def upload_file(profile):
    upload_form = forms.UploadImageForm()
    if upload_form.validate_on_submit():
        file_ = request.files['file']
        title, stored_file = save_file(file_, profile=profile)
        flash('"%s" uploaded successfully.' % title)
        return redirect(_redirect_url_frm_upload(profile.name))
    return render_template('form.html', form=upload_form, profile=profile)


@app.route('/<profile>/new.json', methods=['POST'])
@lastuser.requires_login
@load_model(Profile, {'name': 'profile'}, 'profile',
    permission=['new-file', 'siteadmin'])
def upload_file_json(profile):
    upload_form = forms.UploadImageForm()
    if upload_form.validate_on_submit():
        file_ = request.files['file']
        title, stored_file = save_file(file_, profile=profile)
        update_form = forms.UpdateTitle()
        update_form.title.data = stored_file.title
        form = render_template('edit_title_form.html', form=update_form, formid='edit_title_' + stored_file.name)
        return jsonify(
            status=True, message="%s uploaded successfully" % title, form=form,
            update_url=url_for('update_title_json', profile=profile.name, file=stored_file.name),
            image_data=stored_file.dict_data())
    else:
        response = jsonify(status=False, message=upload_form.errors['file'])
        response.status_code = 403
        return response


@app.route('/<profile>/edit_title', methods=['POST'])
@lastuser.requires_login
@load_model(Profile, {'name': 'profile'}, 'profile',
    permission=['edit', 'siteadmin'])
def edit_title(profile):
    form = forms.EditTitleForm()
    if form.validate_on_submit():
        file_name = request.form.get('file_name')
        q = and_(Profile.userid.in_(g.user.user_organizations_owned_ids()), StoredFile.name == file_name)
        f = StoredFile.query.filter(q).first_or_404()
        f.title = request.form.get('file_title')
        db.session.commit()
        return f.title
    else:
        return form.file_title.errors and form.file_title.errors[0], 400


@app.route('/<profile>/<file>/edit_title.json', methods=['POST'])
@lastuser.requires_login
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (StoredFile, {'name': 'file'}, 'stored_file'),
    permission=['edit', 'siteadmin'])
def update_title_json(profile, stored_file):
    form = forms.UpdateTitle()
    if form.validate_on_submit():
        old_title = stored_file.title
        form.populate_obj(stored_file)
        db.session.commit()
        return jsonify(status=True, message="Title for %s has been updated to %s" % (old_title, stored_file.title), image_data=stored_file.dict_data())
    else:
        update_form = render_template('edit_title_form.html', form=form, formid='edit_title_' + stored_file.name)
        return jsonify(status=False, form=update_form, update_url=url_for('update_title_json', profile=profile.name, file=stored_file.name))


@app.route('/<profile>/view/<image>')
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (StoredFile, {'name': 'image', 'profile': 'profile'}, 'img'),
    permission=['view', 'siteadmin'])
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
    image_url = utils.get_image_url(image, size)
    return redirect(image_url, code=301)


@app.route('/<profile>/delete/<image>', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (StoredFile, {'name': 'image', 'profile': 'profile'}, 'img'),
    permission=['delete', 'siteadmin'])
def delete_file(profile, img):
    form = forms.DeleteImageForm()
    if form.is_submitted():
        delete(img)
        flash("%s is deleted" % img.title)
    else:
        return render_template('delete.html', form=form, file=img, profile=profile)
    return redirect(url_for('profile_view', profile=profile.name))