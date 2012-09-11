# -*- coding: utf-8 -*-
import os.path
from uuid import uuid4
from flask import render_template, request, flash, g, jsonify, make_response
from imgee import app, uploadedfiles
from imgee.forms import UploadForm
from imgee.models import StoredFile, Thumbnail, db, Profile
from imgee.views.login import lastuser, make_profiles
from imgee.storage import upload, is_image, create_thumbnail, convert_size


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
@lastuser.resource_handler('imgee/upload')
def upload_files(callerinfo):
    profileid = request.args.get('profileid', g.user.userid)
    make_profiles()
    if profileid not in g.user.user_organizations_owned_ids():
        return jsonify({'error': 'You do not have permission to access this resource'})
    if request.files.get('stored_file', None):
        filename = uploadedfiles.save(request.files['stored_file'], name=os.path.basename(request.files['stored_file'].filename))
        profile = Profile.query.filter_by(userid=profileid).first()
        stored_file = StoredFile(name=uuid4().hex, title=filename, profile=profile)
        db.session.add(stored_file)
        db.session.commit()
        upload(stored_file.name, stored_file.title)
        return jsonify({'id':  stored_file.name})
    return jsonify({'error': 'No file was uploaded'})


@app.route('/list')
@lastuser.resource_handler('imgee/list')
def list_files(callerinfo):
    profileid = request.args.get('profileid', g.user.userid)
    make_profiles()
    if profileid in g.user.user_organizations_owned_ids():
        files = StoredFile.query.filter(Profile.userid == profileid).all()
        file_list = {'files': [{'name': x.title, 'url': '%s/%s' % (app.config['MEDIA_DOMAIN'], x.name)} for x in files]}
        return jsonify(file_list)
    return jsonify({'error': 'You do not have permission to access this resource'})


@app.route('/file/<filename>')
@lastuser.resource_handler('imgee/thumbnail')
def get_thumbnail(filename):
    make_profiles()
    size = request.args.get('size')
    if not size:
        return jsonify({'error': 'Size not specified'})
    uploadedfile = StoredFile.query.filter_by(name=filename).first()
    if not is_image(uploadedfile.name):
        return jsonify({'error': 'File is not an image'})
    existing_thumnail = Thumbnail.query.filter_by(size=size, uploadedfile=uploadedfile).first()
    if existing_thumbnail:
        return jsonify({'url': '%s/%s' % (app.config['MEDIA_DOMAIN'], existing_thumnail.name)})
    converted_size = convert_size(size)
    if not converted_size:
        return jsonify({'error': 'The size is invalid'})
    new_thumbnail = create_thumbnail(uploadedfile, converted_size)
    if new_thumbnail:
        return jsonify({'url': '%s/%s' % (app.config['MEDIA_DOMAIN'], new_thumnail.name)})
    return jsonify({'error': 'Thumbnail creation error'})
