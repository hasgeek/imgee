# -*- coding: utf-8 -*-
from uuid import uuid4
from flask import render_template, request, flash, g
from imgee import app, uploadedfiles
from imgee.forms import UploadForm
from imgee.models import UploadedFile, db
from imgee.views.login import lastuser
from imgee.storage import upload


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=('GET', 'POST'))
@lastuser.requires_login
def upload_images():
    form = UploadForm(request.form)
    if form.validate_on_submit():
        filename = uploadedfiles.save(request.files['uploaded_file'])
        uploaded_file = UploadedFile(name=uuid4().hex, title=filename, user=g.user)
        db.session.add(uploaded_file)
        db.session.commit()
        upload(uploaded_file.name, uploaded_file.title)
        flash("File saved.")
    elif request.method == 'POST':
        flash("There was an error")
    return render_template('form.html', form=form)

