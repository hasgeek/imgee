from flask import jsonify, request, Blueprint, url_for
from werkzeug.exceptions import HTTPException
from coaster.views import load_model, load_models
import os
from urlparse import urljoin

from imgee import app, lastuser
from imgee.models import db, StoredFile, Profile
import async, utils, storage

api = Blueprint('api', __name__)

class Status(object):
    ok = 'OK'
    in_process = 'PROCESSING'
    notfound = 'NOT FOUND'


@api.route('/file/<imgname>.json')
def get_image_json(imgname):
    try:
        image = StoredFile.query.filter_by(name=imgname).first_or_404()
    except HTTPException:
        return jsonify({"status": Status.notfound, "status_code": 404,
                            "error": "Image with name '%s' doesn't exist." % imgname})

    size = request.args.get('size')
    try:
        url = utils.get_image_url(image, size)
    except async.StillProcessingException as e:
        imgname = e.args[0]
        url = utils.get_url(imgname)
        status = Status.in_process
    else:
        status = Status.ok
    imgee_url = urljoin(request.host_url, url_for('get_image', image=image.name, size=size))

    d = dict(url=url, status=status, imgee_url=imgee_url, status_code=200)
    return jsonify(d)


@api.route('/<profilename>/new.json', methods=['POST'])
def upload_file_json(profilename):
    try:
        profile = Profile.query.filter_by(name=profilename).first_or_404()
    except HTTPException:
        return jsonify({"status": Status.notfound, "status_code": 404,
                        "error": "Profile with name '%s' doesn't exist." % profilename})

    file_ = request.files['file']
    title, job = storage.save(file_, profile=profile)
    try:
        imgname = async.get_async_result(job)
    except async.StillProcessingException as e:
        imgname = e.args[0]
        status = Status.in_process
    else:
        status = Status.ok

    url = utils.get_url(imgname)
    imgname = os.path.splitext(imgname)[0]
    imgee_url = urljoin(request.host_url, url_for('get_image', image=imgname))
    d = dict(url=url, status=status, imgee_url=imgee_url, status_code=200)
    return jsonify(d)

