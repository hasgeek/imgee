# -*- coding: utf-8 -*-
import os.path
from uuid import uuid4
from flask import render_template, request, flash, g, jsonify, make_response, redirect
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
        filename = uploadedfiles.save(request.files['stored_file'])
        profile = Profile.query.filter_by(userid=profileid).first()
        stored_file = StoredFile(name=uuid4().hex, title=os.path.basename(request.files['stored_file'].filename), profile=profile)
        db.session.add(stored_file)
        db.session.commit()
        upload(stored_file.name, filename)
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
def get_thumbnail(filename):
    make_profiles()
    size = request.args.get('size')
    stored_file = StoredFile.query.filter_by(name=filename).first()
    converted_size = convert_size(size)
    if not size or is_image(uploadedfile.name) or not converted_size:
        return redirect('%s/%s' % (app.config['MEDIA_DOMAIN'], stored_file.name))
    existing_thumnail = Thumbnail.query.filter_by(size=size, uploadedfile=uploadedfile).first()
    if existing_thumbnail:
        return redirect('%s/%s' % (app.config['MEDIA_DOMAIN'], existing_thumnail.name))
    new_thumbnail = create_thumbnail(uploadedfile, converted_size)
    if new_thumbnail:
        return redirect('%s/%s' % (app.config['MEDIA_DOMAIN'], new_thumnail.name))
    return redirect('%s/%s' % (app.config['MEDIA_DOMAIN'], stored_file.name))
