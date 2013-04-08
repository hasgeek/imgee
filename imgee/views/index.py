# -*- coding: utf-8 -*-
import os.path
from werkzeug import secure_filename
from uuid import uuid4
from flask import render_template, request, g, jsonify, abort, send_from_directory, redirect
from urlparse import urljoin

from imgee import app, forms
from imgee.models import StoredFile, db, Profile
from imgee.views.login import lastuser, make_profiles, login_required
from imgee.storage import delete_on_s3, save, get_resized_image, get_file_type

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new', methods=('GET', 'POST'))
@lastuser.resource_handler('imgee/upload')
@login_required
def upload_files():
    profileid = g.user.userid
    make_profiles()
    if profileid not in g.user.user_organizations_owned_ids():
        return jsonify({'error': 'You do not have permission to access this resource'})

    upload_form = forms.UploadForm()
    if upload_form.validate_on_submit():
        filename = secure_filename(request.files['uploaded_file'].filename)
        uniq_name = uuid4().hex
        profile = Profile.query.filter_by(userid=profileid).first()
        stored_file = StoredFile(name=uniq_name, title=filename, profile=profile)
        db.session.add(stored_file)
        db.session.commit()
        content_type = get_file_type(filename)
        save(request.files['uploaded_file'], stored_file.name, content_type=content_type)
        return jsonify({'id':  stored_file.name})
    # form invalid or request.method == 'GET'
    return render_template('form.html', form=upload_form)

@app.route('/list')
@lastuser.resource_handler('imgee/list')
@login_required
def list_files():
    profileid = request.args.get('profileid', g.user.userid)
    make_profiles()
    if profileid in g.user.user_organizations_owned_ids():
        files = StoredFile.query.filter(Profile.userid == profileid).all()
        file_list = {'files': [{'name': x.title, 'url': '%s/%s' % (app.config['MEDIA_DOMAIN'], x.name)} for x in files]}
        return jsonify(file_list)
    return jsonify({'error': 'You do not have permission to access this resource'})

@app.route('/file/<img_name>')
def get_image(img_name):
    make_profiles()
    img = StoredFile.query.filter_by(name=img_name).first()
    if not img: abort(404)
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
@lastuser.resource_handler('imgee/delete')
@login_required
def delete_files(img_name):
    profileid = g.user.userid
    make_profiles()
    if profileid in g.user.user_organizations_owned_ids():
        form = forms.DeleteForm()
        if form.validate_on_submit():
            stored_file = StoredFile.query.filter_by(name=img_name).first()
            if stored_file:
                delete_on_s3(stored_file)
                db.session.delete(stored_file)
                db.session.commit()
                return jsonify({'success': 'File deleted'})
            return jsonify({'error': 'No file found'})
        return render_template('delete.html', form=form, filename=img_name)
    return jsonify({'error': 'You do not have permission to access this resource'})
