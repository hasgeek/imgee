# -*- coding: utf-8 -*-

import os.path
from uuid import uuid4
import magic
from PIL import Image
from urlparse import urljoin

from boto import connect_s3
from boto.s3.bucket import Bucket
from boto.s3.key import Key

from flask import request

import imgee
from imgee import app

ALLOWED_MIMETYPES = {
    'image/jpg': {'allowed_extns':['.jpe', '.jpg', '.jpeg'], 'extn': '.jpeg'},
    'image/jpe': {'allowed_extns':['.jpe', '.jpg', '.jpeg'], 'extn': '.jpeg'},
    'image/jpeg': {'allowed_extns':['.jpe', '.jpg', '.jpeg'], 'extn': '.jpeg'},
    'image/pjpeg': {'allowed_extns':['.jpe', '.jpg', '.jpeg'], 'extn': '.jpeg'},
    'image/png': {'allowed_extns':['.png'], 'extn': '.png'},
    'image/gif': {'allowed_extns':['.gif'], 'extn': '.gif'},
    'image/vnd.adobe.photoshop': {'allowed_extns':['.psd'], 'extn': '.psd'},
    'application/pdf': {'allowed_extns':['.pdf', '.ai'], 'extn': ['.pdf', '.ai']},
    'application/illustrator': {'allowed_extns':['.ai'], 'extn': '.ai'},
    'application/postscript': {'allowed_extns':['.eps', 'ai'], 'extn': ['.pdf', '.ai']},
    'image/svg+xml': {'allowed_extns':['.svg'], 'extn': '.svg'},
    'image/bmp': {'allowed_extns':['.bmp'], 'extn': '.bmp'},
    'image/x-bmp': {'allowed_extns':['.bmp'], 'extn': '.bmp'},
    'image/x-bitmap': {'allowed_extns':['.bmp'], 'extn': '.bmp'},
    'image/x-xbitmap': {'allowed_extns':['.bmp'], 'extn': '.bmp'},
    'image/x-win-bitmap': {'allowed_extns':['.bmp'], 'extn': '.bmp'},
    'image/x-windows-bmp': {'allowed_extns':['.bmp'], 'extn': '.bmp'},
    'image/ms-bmp': {'allowed_extns':['.bmp'], 'extn': '.bmp'},
    'image/x-ms-bmp': {'allowed_extns':['.bmp'], 'extn': '.bmp'},
    'application/bmp': {'allowed_extns':['.bmp'], 'extn': '.bmp'},
    'application/x-bmp': {'allowed_extns':['.bmp'], 'extn': '.bmp'},
    'application/x-win-bitmap': {'allowed_extns':['.bmp'], 'extn': '.bmp'},
    'application/cdr': {'allowed_extns':['.cdr'], 'extn': '.cdr'},
    'application/coreldraw': {'allowed_extns':['.cdr'], 'extn': '.cdr'},
    'application/x-cdr': {'allowed_extns':['.cdr'], 'extn': '.cdr'},
    'application/x-coreldraw': {'allowed_extns':['.cdr'], 'extn': '.cdr'},
    'image/cdr': {'allowed_extns':['.cdr'], 'extn': '.cdr'},
    'image/x-cdr': {'allowed_extns':['.cdr'], 'extn': '.cdr'},
    'application/eps': {'allowed_extns':['.eps'], 'extn': '.eps'},
    'application/x-eps': {'allowed_extns':['.eps'], 'extn': '.eps'},
    'image/eps': {'allowed_extns':['.eps'], 'extn': '.eps'},
    'image/x-eps': {'allowed_extns':['.eps'], 'extn': '.eps'},
    'image/tif': {'allowed_extns':['.tif', '.tiff'], 'extn': ['.tif', 'tiff']},
    'image/x-tif': {'allowed_extns':['.tif', '.tiff'], 'extn': ['.tif', 'tiff']},
    'image/tiff': {'allowed_extns':['.tif', '.tiff'], 'extn': ['.tif', 'tiff']},
    'image/x-tiff': {'allowed_extns':['.tif', '.tiff'], 'extn': ['.tif', 'tiff']},
    'application/tif': {'allowed_extns':['.tif', '.tiff'], 'extn': ['.tif', 'tiff']},
    'application/x-tif': {'allowed_extns':['.tif', '.tiff'], 'extn': ['.tif', 'tiff']},
    'application/tiff': {'allowed_extns':['.tif', '.tiff'], 'extn': ['.tif', 'tiff']},
    'application/x-tiff': {'allowed_extns':['.tif', '.tiff'], 'extn': ['.tif', 'tiff']}
}

def newid():
    return unicode(uuid4().hex)


def get_media_domain():
    scheme = request.scheme
    return '%s:%s' % (scheme, app.config.get('MEDIA_DOMAIN'))

def path_for(img_name):
    return os.path.join(app.config['UPLOADED_FILES_DEST'], img_name)


# -- mimetypes and content types

def guess_extension(mimetype, orig_extn):
    if mimetype in ALLOWED_MIMETYPES:
        if orig_extn not in ALLOWED_MIMETYPES[mimetype]['orig_extn']:
            if type(ALLOWED_MIMETYPES[mimetype]['extn']) == str:
                orig_extn = ALLOWED_MIMETYPES[mimetype]['extn']
            else:
                orig_extn = ALLOWED_MIMETYPES[mimetype]['extn'][0]
        if type(ALLOWED_MIMETYPES[mimetype]['extn']) == list:
            if orig_extn in ALLOWED_MIMETYPES[mimetype]['extn']:
                return orig_extn
            else:
                return ALLOWED_MIMETYPES[mimetype]['extn'][0]
        else:
            return ALLOWED_MIMETYPES[mimetype]['extn']


def get_file_type(fp):
    fp.seek(0)
    data = fp.read()
    fp.seek(0)
    return magic.from_buffer(data, mime=True)


def is_file_allowed(fp):
    return get_file_type(fp) in ALLOWED_MIMETYPES

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
    return get_url(thumbnail, extn)
