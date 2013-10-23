from flask import jsonify, request, Blueprint
from coaster.views import load_model, load_models

from imgee import app, lastuser
from imgee.models import db, StoredFile, Profile
import async, utils, storage

api = Blueprint('api', __name__)

class Status(object):
    ok = 'OK'
    in_process = 'Processing'


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
    d = dict(url=url, status=status)
    return jsonify(d)


@api.route('/<profile>/new.json', methods=['POST'])
@load_model(Profile, {'name': 'profile'}, 'profile',
    permission=['new-file', 'siteadmin']), addlperms=lastuser.permissions)
def upload_file_json(profile):
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
    d = dict(url=url, status=status)
    return jsonify(d)

