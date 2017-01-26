# -*- coding: utf-8 -*-
import os.path
import time
from flask import (render_template, request, g, url_for,
    redirect, flash, Response, jsonify)
from sqlalchemy import and_, not_

from coaster.views import load_model, load_models
from imgee import app, forms, lastuser
from imgee.models import StoredFile, db, Profile, Label
from imgee.storage import delete, save, clean_local_cache
from imgee.utils import get_media_domain, not_in_deleteQ, ALLOWED_MIMETYPES
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

def stored_file_data(stored_file):
    return dict(
        title=stored_file.title,
        uploaded=stored_file.created_at.strftime('%B %d, %Y'),
        filesize=app.jinja_env.filters['filesizeformat'](stored_file.size),
        imgsize='%s x %s' % (stored_file.width, stored_file.height),
        url=url_for('view_image', profile=stored_file.profile.name, image=stored_file.name),
        thumb_url=url_for('get_image', image=stored_file.name, size=app.config.get('THUMBNAIL_SIZE')))

def generate_thumbs(image):
    def generate_thumb(image, size):
        try:
            utils.get_image_url(image, size)
        except async.StillProcessingException:
            pass
    generate_thumb(image, '75x75')
    sizes = [250, 400, 430, 600, 770]
    for size in sizes:
        if size > image.width:
            break
        else:
            generate_thumb(image, str(size))

@app.route('/<profile>/new', methods=['GET', 'POST'])
@load_model(Profile, {'name': 'profile'}, 'profile',
    permission=['new-file', 'siteadmin'], addlperms=lastuser.permissions)
def upload_file(profile):
    upload_form = forms.UploadImageForm()
    if upload_form.validate_on_submit():
        file_ = request.files['file']
        title, stored_file = save(file_, profile=profile)
        flash('"%s" uploaded successfully.' % title)
        return redirect(_redirect_url_frm_upload(profile.name))
    return render_template('form.html', form=upload_form, profile=profile)

@app.route('/<profile>/new.json', methods=['POST'])
@load_model(Profile, {'name': 'profile'}, 'profile',
    permission=['new-file', 'siteadmin'], addlperms=lastuser.permissions)
def upload_file_json(profile):
    upload_form = forms.UploadImageForm()
    if upload_form.validate_on_submit():
        file_ = request.files['file']
        title, stored_file = save(file_, profile=profile)
        update_form = forms.UpdateTitle()
        update_form.title.data = stored_file.title
        form = render_template('edit_title_form.html', form=update_form, formid='edit_title_' + stored_file.name)
        return jsonify(
            status=True, message="%s uploaded successfully" % title, form=form,
            update_url=url_for('update_title_json', profile=profile.name,file=stored_file.name),
            image_data=stored_file_data(stored_file))
    else:
        response = jsonify(status=False, message=upload_form.errors['file'])
        response.status_code = 403
        return response

@app.route('/<profile>/popup')
@load_model(Profile, {'name': 'profile'}, 'profile',
    permission=['view', 'siteadmin'], addlperms=lastuser.permissions)
def pop_up_gallery(profile):
    label = request.args.get('label')
    files = profile.stored_files
    if label:
        files = files.join(StoredFile.labels).filter(Label.name==label)
    files = files.order_by('stored_file.created_at desc').all()
    files = not_in_deleteQ(files)
    form = forms.UploadImageForm()
    cp_form = forms.ChangeProfileForm()
    cp_form.profiles.choices = [(p.id, p.name) for p in g.user.profiles]
    return render_template('pop_up_gallery.html', files=files, label=label,
                profile=profile, uploadform=form, cp_form=cp_form)


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

@app.route('/<profile>/<file>/edit_title.json', methods=['POST'])
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (StoredFile, {'name': 'file'}, 'stored_file'),
    permission=['edit', 'siteadmin'], addlperms=lastuser.permissions)
def update_title_json(profile, stored_file):
    form = forms.UpdateTitle()
    if form.validate_on_submit():
        old_title = stored_file.title
        form.populate_obj(stored_file)
        db.session.commit()
        return jsonify(status=True, message="Title for %s has been updated to %s" % (old_title, stored_file.title), image_data=stored_file_data(stored_file))
    else:
        update_form = render_template('edit_title_form.html', form=form, formid='edit_title_' + stored_file.name)
        return jsonify(status=False, form=update_form, update_url=url_for('update_title_json', profile=profile.name, file=stored_file.name))


@app.route('/<profile>')
@load_model(Profile, {'name': 'profile'}, 'profile')
def profile_view(profile):
    files = profile.stored_files.order_by('created_at desc').all()
    files = not_in_deleteQ(files)
    title_form = forms.EditTitleForm()
    upload_form = forms.UploadImageForm()
    return render_template('profile.html', profile=profile, files=files, uploadform=upload_form, title_form=title_form, mimetypes=ALLOWED_MIMETYPES.keys())


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
    return imgs[pos+1 : pos+1+limit], imgs[:pos][-limit:]

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
    image_url = utils.get_image_url(image, size)
    return redirect(image_url, code=301)


@app.route('/<profile>/delete/<image>', methods=['GET', 'POST'])
@load_models(
    (Profile, {'name': 'profile'}, 'profile'),
    (StoredFile, {'name': 'image', 'profile': 'profile'}, 'img'),
    permission=['delete', 'siteadmin'], addlperms=lastuser.permissions)
def delete_file(profile, img):
    form = forms.DeleteImageForm()
    if form.is_submitted():
        delete(img)
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
