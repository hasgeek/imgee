# -*- coding: utf-8 -*-
from uuid import uuid4
from flask import render_template, request, flash, g, jsonify
from imgee import app, uploadedfiles
from imgee.forms import UploadForm
from imgee.models import UploadedFile, db
from imgee.views.login import lastuser
from imgee.storage import upload


@app.route('/upload', methods=('GET', 'POST'))
@lastuser.requires_login
def upload_files():
    if request.files['uploaded_file']:
        filename = uploadedfiles.save(request.files['uploaded_file'])
        uploaded_file = UploadedFile(name=uuid4().hex, title=filename, user=g.user)
        db.session.add(uploaded_file)
        db.session.commit()
        upload(uploaded_file.name, uploaded_file.title)
        return jsonify({'url': '%s/%s' % (app.config['MEDIA_DOMAIN'], uploaded_file.name)})


@app.route('/list')
@lastuser.requires_login
def list_files():
    files = UploadedFile.query.filter_by(user=g.user).all()
    file_list = {'files': [{'name': x.title, 'url': '%s/%s' % (app.config['MEDIA_DOMAIN'], x.name)} for x in files]}
    return jsonify(file_list)
