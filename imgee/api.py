from flask import jsonify, request, Blueprint, url_for
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
    accepted = 'ACCEPTED'

@api.errorhandler(404)
def error404(error):
    return jsonify({"status": Status.notfound, "status_code": 404})

@api.route('/file/<image>.json')
@load_model(StoredFile, {'name': 'image'}, 'image')
def get_image_json(image):
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


@api.route('/<profile>/new.json', methods=['POST'])
@load_model(Profile, {'name': 'profile'}, 'profile')
@lastuser.resource_handler('imgee/new')
def upload_file_json(callerinfo, profile):
    file_ = request.files['file']
    title = request.form.get('title')
    title, stored_file = storage.save(file_, profile=profile, title=title)
    imgname = stored_file.name
    url = utils.get_url(imgname)
    imgname = os.path.splitext(imgname)[0]
    imgee_url = urljoin(request.host_url, url_for('get_image', image=imgname))
    d = dict(url=url, status=status, imgee_url=imgee_url, status_code=200)
    return jsonify(d)

