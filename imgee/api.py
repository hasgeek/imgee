from flask import jsonify, request
from coaster.views import load_model, load_models

from imgee import app, lastuser
from imgee.models import db, StoredFile, Profile
import async, utils, storage


class Status(object):
    ok = 'OK'
    in_process = 'Processing'


@app.route('/api/file/<image>.json')
@load_model(StoredFile, {'name': 'image'}, 'image')
def get_image_json(image):
    size = request.args.get('size')
    d = {}
    try:
        d['url'] = utils.get_image_url(image, size)
    except async.StillProcessingException as e:
        imgname = e.args[0]
        d['url'] = utils.get_url(imgname)
        d['status'] = Status.in_process
    else:
        d['status'] = Status.ok

    return jsonify(d)


@app.route('/api/<profile>/new.json', methods=['POST'])
@load_model(Profile, {'name': 'profile'}, 'profile'),
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

