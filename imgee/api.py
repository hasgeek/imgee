from flask import jsonify, request
from coaster.views import load_model, load_models

from imgee import app
from imgee.models import db, StoredFile
import async, utils


@app.route('/api/file/<image>')
@load_model(StoredFile, {'name': 'image'}, 'image')
def get_image_json(image):
    size = request.args.get('size')
    d = {}
    try:
        d['url'] = utils.get_image_url(image, size)
        d['status'] = 'OK'
    except async.StillProcessingException as e:
        imgname = e.args[0]
        d['url'] = utils.get_url(imgname)
        d['status'] = 'Processing'
    return jsonify(d)


