# -*- coding: utf-8 -*-
from uuid import uuid4
from flask import render_template, request, flash, g, jsonify, make_response
from imgee import app, uploadedfiles
from imgee.forms import UploadForm
from imgee.models import StoredFile, Thumbnail, db
from imgee.views.login import lastuser
from imgee.storage import upload, is_image, create_thumbnail, convert_size


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=('GET', 'POST'))
@lastuser.resource_handler
def upload_files():
    if request.files['uploaded_file']:
        filename = uploadedfiles.save(request.files['uploaded_file'])
        uploaded_file = StoredFile(name=uuid4().hex, title=filename, user=g.user)
        db.session.add(uploaded_file)
        db.session.commit()
        upload(uploaded_file.name, uploaded_file.title)
        return jsonify({'idl':  uploaded_file.name})
    return jsonify({'error': 'No file was uploaded'})


@app.route('/list')
@lastuser.resource_handler
def list_files():
    files = StoredFile.query.filter_by(user=g.user).all()
    file_list = {'files': [{'name': x.title, 'url': '%s/%s' % (app.config['MEDIA_DOMAIN'], x.name)} for x in files]}
    return jsonify(file_list)


@app.route('/file/<filename>')
@lastuser.resource_handler
def get_thumbnail(filename):
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
