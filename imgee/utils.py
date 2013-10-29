# -*- coding: utf-8 -*-

import os.path
from uuid import uuid4
import mimetypes
from PIL import Image
from urlparse import urljoin

from boto import connect_s3
from boto.s3.bucket import Bucket
from boto.s3.key import Key

from flask import request

import imgee
from imgee import app

def newid():
    return unicode(uuid4().hex)


def get_media_domain():
    scheme = request.scheme
    return '%s:%s' % (scheme, app.config.get('MEDIA_DOMAIN'))

def path_for(img_name):
    return os.path.join(app.config['UPLOADED_FILES_DEST'], img_name)


# -- mimetypes and content types

def guess_extension(mimetype):
    if mimetype in ('image/jpg', 'image/jpe', 'image/jpeg'):
        return '.jpeg'    # guess_extension returns .jpe, which PIL doesn't like
    return mimetypes.guess_extension(mimetype)


def get_file_type(filename):
    return mimetypes.guess_type(filename)[0]

# -- s3 related --

def get_s3_bucket():
    conn = connect_s3(app.config['AWS_ACCESS_KEY'], app.config['AWS_SECRET_KEY'])
    bucket = Bucket(conn, app.config['AWS_BUCKET'])
    return bucket


def get_s3_folder(f=''):
    f = f or app.config.get('AWS_FOLDER', '')
    if f and not f.endswith('/'):
        f = f + '/'
    return f or ''


def download_frm_s3(img_name):
    local_path = path_for(img_name)
    if not os.path.exists(local_path):
        bucket = get_s3_bucket()
        k = Key(bucket)
        k.key = img_name
        k.get_contents_to_filename(local_path)
    return local_path


def not_in_deleteQ(imgs):
    # filters out the images which are queued for deletion and returns the remaining
    return [i for i in imgs if not i.is_queued_for_deletion()]


# -- image details --

def get_width_height(img_path):
    try:
        img = Image.open(img_path)
    except IOError:
        return (0, 0)
    else:
        return img.size


def image_formats():
    return '.jpg .jpe .jpeg .png .gif .bmp'.split()


def get_url(img_name, extn=''):
    img_name = get_s3_folder() + img_name + extn
    media_domain = get_media_domain()
    return urljoin(media_domain, img_name)


def get_image_url(image, size=None):
    extn = image.extn
    if size and (extn in image_formats()):
        r = imgee.storage.get_resized_image(image, size)
        img_name = imgee.async.get_async_result(r)
    else:
        img_name = image.name
    return get_url(img_name, extn)


def get_thumbnail_url(image):
    extn = image.extn
    if extn in image_formats():
        tn_size = app.config.get('THUMBNAIL_SIZE')
        r = imgee.storage.get_resized_image(image, tn_size, is_thumbnail=True)
        thumbnail = imgee.async.get_async_result(r)
    else:
        thumbnail = app.config.get('UNKNOWN_FILE_THUMBNAIL')
    return get_url(image.name, extn)
