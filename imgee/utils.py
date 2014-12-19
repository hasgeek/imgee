# -*- coding: utf-8 -*-

import os.path
from uuid import uuid4
import magic
from urlparse import urljoin
from subprocess import check_output, CalledProcessError

from boto import connect_s3
from boto.s3.bucket import Bucket
from boto.s3.key import Key

from flask import request

import imgee
from imgee import app

ALLOWED_MIMETYPES = {
    'image/jpg': {'allowed_extns': [u'.jpe', u'.jpg', u'.jpeg'], 'extn': u'.jpeg'},
    'image/jpe': {'allowed_extns': [u'.jpe', u'.jpg', u'.jpeg'], 'extn': u'.jpeg'},
    'image/jpeg': {'allowed_extns': [u'.jpe', u'.jpg', u'.jpeg'], 'extn': u'.jpeg'},
    'image/pjpeg': {'allowed_extns': [u'.jpe', u'.jpg', u'.jpeg'], 'extn': u'.jpeg'},
    'image/png': {'allowed_extns': [u'.png'], 'extn': u'.png'},
    'image/gif': {'allowed_extns': [u'.gif'], 'extn': u'.gif'},
    'image/vnd.adobe.photoshop': {'allowed_extns': [u'.psd'], 'extn': u'.psd', 'thumb_extn': False},
    'application/pdf': {'allowed_extns': [u'.pdf', u'.ai'], 'extn': [u'.pdf', u'.ai'], 'thumb_extn': u'.png'},
    'application/illustrator': {'allowed_extns': [u'.ai'], 'extn': u'.ai', 'thumb_extn': u'.png'},
    'application/postscript': {'allowed_extns': [u'.eps'], 'extn': u'.eps', 'thumb_extn': u'.png'},
    'image/svg+xml': {'allowed_extns': [u'.svg'], 'extn': u'.svg', 'thumb_extn': u'.png', 'processor': 'rsvg-convert'},
    'application/x-gzip': {'allowed_extns': [u'.svgz'], 'extn': u'.svgz', 'thumb_extn': u'.png', 'processor': 'rsvg-convert'},
    'image/bmp': {'allowed_extns': [u'.bmp'], 'extn': u'.bmp', 'thumb_extn': u'.jpeg'},
    'image/x-bmp': {'allowed_extns': [u'.bmp'], 'extn': u'.bmp', 'thumb_extn': u'.jpeg'},
    'image/x-bitmap': {'allowed_extns': [u'.bmp'], 'extn': u'.bmp', 'thumb_extn': u'.jpeg'},
    'image/x-xbitmap': {'allowed_extns': [u'.bmp'], 'extn': u'.bmp', 'thumb_extn': u'.jpeg'},
    'image/x-win-bitmap': {'allowed_extns': [u'.bmp'], 'extn': u'.bmp', 'thumb_extn': u'.jpeg'},
    'image/x-windows-bmp': {'allowed_extns': [u'.bmp'], 'extn': u'.bmp', 'thumb_extn': u'.jpeg'},
    'image/ms-bmp': {'allowed_extns': [u'.bmp'], 'extn': u'.bmp', 'thumb_extn': u'.jpeg'},
    'image/x-ms-bmp': {'allowed_extns': [u'.bmp'], 'extn': u'.bmp', 'thumb_extn': u'.jpeg'},
    'application/bmp': {'allowed_extns': [u'.bmp'], 'extn': u'.bmp', 'thumb_extn': u'.jpeg'},
    'application/x-bmp': {'allowed_extns': [u'.bmp'], 'extn': u'.bmp', 'thumb_extn': u'.jpeg'},
    'application/x-win-bitmap': {'allowed_extns': [u'.bmp'], 'extn': u'.bmp', 'thumb_extn': u'.jpeg'},
    'application/cdr': {'allowed_extns': [u'.cdr'], 'extn': u'.cdr', 'thumb_extn': False},
    'application/coreldraw': {'allowed_extns': [u'.cdr'], 'extn': u'.cdr', 'thumb_extn': False},
    'application/x-cdr': {'allowed_extns': [u'.cdr'], 'extn': u'.cdr', 'thumb_extn': False},
    'application/x-coreldraw': {'allowed_extns': [u'.cdr'], 'extn': u'.cdr', 'thumb_extn': False},
    'image/cdr': {'allowed_extns': [u'.cdr'], 'extn': u'.cdr', 'thumb_extn': False},
    'image/x-cdr': {'allowed_extns': [u'.cdr'], 'extn': u'.cdr', 'thumb_extn': False},
    'application/eps': {'allowed_extns': [u'.eps'], 'extn': u'.eps', 'thumb_extn': u'.png'},
    'application/x-eps': {'allowed_extns': [u'.eps'], 'extn': u'.eps', 'thumb_extn': u'.png'},
    'image/eps': {'allowed_extns': [u'.eps'], 'extn': u'.eps', 'thumb_extn': u'.png'},
    'image/x-eps': {'allowed_extns': [u'.eps'], 'extn': u'.eps', 'thumb_extn': u'.png'},
    'image/tif': {'allowed_extns': [u'.tif', u'.tiff'], 'extn': [u'.tif', u'.tiff'], 'thumb_extn': u'.png'},
    'image/x-tif': {'allowed_extns': [u'.tif', u'.tiff'], 'extn': [u'.tif', u'.tiff'], 'thumb_extn': u'.png'},
    'image/tiff': {'allowed_extns': [u'.tif', u'.tiff'], 'extn': [u'.tif', u'.tiff'], 'thumb_extn': u'.png'},
    'image/x-tiff': {'allowed_extns': [u'.tif', u'.tiff'], 'extn': [u'.tif', u'.tiff'], 'thumb_extn': u'.png'},
    'application/tif': {'allowed_extns': [u'.tif', u'.tiff'], 'extn': [u'.tif', u'.tiff'], 'thumb_extn': u'.png'},
    'application/x-tif': {'allowed_extns': [u'.tif', u'.tiff'], 'extn': [u'.tif', u'.tiff'], 'thumb_extn': u'.png'},
    'application/tiff': {'allowed_extns': [u'.tif', u'.tiff'], 'extn': [u'.tif', u'.tiff'], 'thumb_extn': u'.png'},
    'application/x-tiff': {'allowed_extns': [u'.tif', u'.tiff'], 'extn': [u'.tif', u'.tiff'], 'thumb_extn': u'.png'}
}

EXTNS = []
for mimetype, data in ALLOWED_MIMETYPES.iteritems():
    if type(data['extn']) == list:
        for extn in data['extn']:
            EXTNS.append(extn)
    else:
        EXTNS.append(data['extn'])
EXTNS = list(set(EXTNS))


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
        if orig_extn not in ALLOWED_MIMETYPES[mimetype]['allowed_extns']:
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
        o = check_output('identify -quiet -ping -format "%wx%h" {}'.format(img_path), shell=True)
        return tuple(int(dim) for dim in o.split('x'))
    except CalledProcessError:
        return (0, 0)


def get_url(img_name, extn=''):
    img_name = get_s3_folder() + img_name + extn
    media_domain = get_media_domain()
    return urljoin(media_domain, img_name)


def get_no_previews_url(size):
    if size in ('75x75', '75'):
        return '/static/img/no-preview-75.png'
    else:
        return '/static/img/no-preview-800.png'


def get_image_url(image, size=None):
    extn = image.extn
    if size and extn in EXTNS:
        if image.no_previews:
            return get_no_previews_url(size)
        r = imgee.storage.get_resized_image(image, size)
        img_name = imgee.async.get_async_result(r)
    else:
        img_name = image.name
    if size and 'thumb_extn' in ALLOWED_MIMETYPES[image.mimetype]:
        extn = ALLOWED_MIMETYPES[image.mimetype]['thumb_extn']
    return get_url(img_name, extn)


def get_thumbnail_url(image):
    extn = image.extn
    if extn in EXTNS:
        tn_size = app.config.get('THUMBNAIL_SIZE')
        r = imgee.storage.get_resized_image(image, tn_size, is_thumbnail=True)
        thumbnail = imgee.async.get_async_result(r)
    else:
        thumbnail = app.config.get('UNKNOWN_FILE_THUMBNAIL')
    return get_url(thumbnail, extn)
