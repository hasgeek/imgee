# -*- coding: utf-8 -*-
import os.path
from werkzeug import secure_filename
from uuid import uuid4
from flask import render_template, request, g, jsonify, redirect
from flask.ext.uploads import save

from imgee import app, forms
from imgee.models import StoredFile, Thumbnail, db, Profile
from imgee.views.login import lastuser, make_profiles, login_required
from imgee.storage import is_image, create_thumbnail, split_size, delete_image

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
        extn = os.path.splitext(filename)[1]
        uniq_name = uuid4().hex + extn
        profile = Profile.query.filter_by(userid=profileid).first()
        stored_file = StoredFile(name=uniq_name, title=filename, profile=profile)
        db.session.add(stored_file)
        db.session.commit()
        save(request.files['uploaded_file'], stored_file.name)
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


@app.route('/file/<filename>')
def get_thumbnail(filename):
    make_profiles()
    size = request.args.get('size', '')
    converted_size = split_size(size)
    stored_file = StoredFile.query.filter_by(name=filename).first()
    if (not size) and is_image(stored_file.name):
        return redirect('%s/%s' % (app.config['MEDIA_DOMAIN'], stored_file.name))
    thumbnail = Thumbnail.query.filter_by(size=size, stored_file=stored_file).first()
    if not thumbnail:
        thumbnail = create_thumbnail(stored_file, converted_size)
    return redirect('%s/%s' % (app.config['MEDIA_DOMAIN'], new_thumbnail.name))

@app.route('/delete', methods=['POST'])
@lastuser.resource_handler('imgee/delete')
@login_required
def delete_files(callerinfo):
    profileid = request.args.get('profileid', g.user.userid)
    fileid = request.args.get('fileid', g.user.userid)
    if not fileid:
        return jsonify({'error': 'No filename given'})
    make_profiles()
    if profileid in g.user.user_organizations_owned_ids():
        stored_file = StoredFile.query.filter_by(name=fileid).first()
        if stored_file:
            delete_image(stored_file)
            db.session.delete(stored_file)
            db.session.commit()
            return jsonify({'success': 'File deleted'})
        return jsonify({'error': 'No file found'})
    return jsonify({'error': 'You do not have permission to access this resource'})
