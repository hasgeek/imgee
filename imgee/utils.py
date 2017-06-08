# -*- coding: utf-8 -*-

import re
import os.path
from subprocess import check_output, CalledProcessError
from urlparse import urljoin

from boto import connect_s3
from boto.s3.bucket import Bucket
from boto.s3.key import Key
import defusedxml.cElementTree as elementtree
from flask import request
import magic
from PIL import Image

from coaster.utils import uuid1mc
from imgee import app

THUMBNAIL_COMMANDS = {
    'inkscape': "inkscape -z -f {src} -e {src}.original.png && convert -quiet -thumbnail {width}x{height} {src}.original.png -colorspace sRGB -quality 75% {dest}",
    'rsvg-convert': "rsvg-convert --width={width} --height={height} --keep-aspect-ratio=TRUE --format={format} {src} > {dest}",
    'convert': "convert -quiet -thumbnail {width}x{height} {src} -colorspace sRGB -quality 75% {dest}",
    'convert-pdf': "convert -quiet -thumbnail {width}x{height} {src}[0] -colorspace sRGB -quality 75% -background white -flatten {dest}",
    'convert-layered': "convert -quiet -thumbnail {width}x{height} {src}[0] -colorspace sRGB -quality 75% {dest}"
}

ALLOWED_MIMETYPES = {
    'image/jpg': {'allowed_extns': [u'.jpe', u'.jpg', u'.jpeg'], 'extn': u'.jpeg'},
    'image/jpe': {'allowed_extns': [u'.jpe', u'.jpg', u'.jpeg'], 'extn': u'.jpeg'},
    'image/jpeg': {'allowed_extns': [u'.jpe', u'.jpg', u'.jpeg'], 'extn': u'.jpeg'},
    'image/pjpeg': {'allowed_extns': [u'.jpe', u'.jpg', u'.jpeg'], 'extn': u'.jpeg'},
    'image/png': {'allowed_extns': [u'.png'], 'extn': u'.png'},
    'image/gif': {'allowed_extns': [u'.gif'], 'extn': u'.gif', 'processor': 'convert-layered'},
    'image/vnd.adobe.photoshop': {'allowed_extns': [u'.psd'], 'extn': u'.psd', 'thumb_extn': '.jpeg', 'processor': 'convert-layered'},
    'application/pdf': {'allowed_extns': [u'.pdf', u'.ai'], 'extn': [u'.pdf', u'.ai'], 'thumb_extn': u'.png', 'processor': 'convert-pdf'},
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
    'application/cdr': {'allowed_extns': [u'.cdr'], 'extn': u'.cdr', 'thumb_extn': '.png', 'processor': 'inkscape'},
    'application/coreldraw': {'allowed_extns': [u'.cdr'], 'extn': u'.cdr', 'thumb_extn': '.png', 'processor': 'inkscape'},
    'application/x-cdr': {'allowed_extns': [u'.cdr'], 'extn': u'.cdr', 'thumb_extn': '.png', 'processor': 'inkscape'},
    'application/x-coreldraw': {'allowed_extns': [u'.cdr'], 'extn': u'.cdr', 'thumb_extn': '.png', 'processor': 'inkscape'},
    'application/vnd.corel-draw': {'allowed_extns': [u'.cdr'], 'extn': u'.cdr', 'thumb_extn': '.png', 'processor': 'inkscape'},
    'image/cdr': {'allowed_extns': [u'.cdr'], 'extn': u'.cdr', 'thumb_extn': '.png', 'processor': 'inkscape'},
    'image/x-cdr': {'allowed_extns': [u'.cdr'], 'extn': u'.cdr', 'thumb_extn': '.png', 'processor': 'inkscape'},
    'image/x-coreldraw': {'allowed_extns': [u'.cdr'], 'extn': u'.cdr', 'thumb_extn': '.png', 'processor': 'inkscape'},
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
    'application/x-tiff': {'allowed_extns': [u'.tif', u'.tiff'], 'extn': [u'.tif', u'.tiff'], 'thumb_extn': u'.png'},
    'image/webp': {'allowed_extns': [u'.webp'], 'extn': '.webp', 'thumb_extn': u'.jpeg'},
    'image/x-xcf': {'allowed_extns': [u'.xcf'], 'extn': '.xcf', 'thumb_extn': u'.jpeg'}
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
    return unicode(uuid1mc().hex)


def get_media_domain(scheme=None):
    scheme = scheme or request.scheme
    return '%s:%s' % (scheme, app.config.get('MEDIA_DOMAIN'))


def get_file_url(scheme=None):
    return ''


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


def is_svg(fp):
    fp.seek(0)
    tag = None
    try:
        for event, el in elementtree.iterparse(fp, ('start',)):
            tag = el.tag
            break
    except elementtree.ParseError:
        pass
    fp.seek(0)
    return tag == '{http://www.w3.org/2000/svg}svg'


def is_animated_gif(local_path):
    is_animated = True
    gif = Image.open(local_path)
    try:
        gif.seek(1)
    except EOFError:
        is_animated = False
    return is_animated


def get_file_type(fp, filename=None):
    fp.seek(0)
    data = fp.read()
    fp.seek(0)
    result = magic.from_buffer(data, mime=True)
    if result in ('text/plain', 'text/xml', 'application/xml'):
        if is_svg(fp):
            return 'image/svg+xml'
    return result


def is_file_allowed(fp, provided_mimetype=None, filename=None):
    fp.seek(0)
    data = fp.read()
    fp.seek(0)
    if len(data) == 0:
        # reject files with zero size
        return False
    return get_file_type(fp, filename) in ALLOWED_MIMETYPES


# -- s3 related --
def get_s3_connection():
    return connect_s3(app.config['AWS_ACCESS_KEY'], app.config['AWS_SECRET_KEY'])


def get_s3_bucket():
    conn = get_s3_connection()
    bucket = Bucket(conn, app.config['AWS_BUCKET'])
    return bucket


def get_s3_folder(f=''):
    f = f or app.config.get('AWS_FOLDER', '')
    if f and not f.endswith('/'):
        f = f + '/'
    return f or ''


def exists_in_s3(thumb):
    folder = get_s3_folder()
    bucket = get_s3_bucket()
    extn = thumb.stored_file.extn
    if 'thumb_extn' in ALLOWED_MIMETYPES[thumb.stored_file.mimetype]:
        extn = ALLOWED_MIMETYPES[thumb.stored_file.mimetype]['thumb_extn']
    key = os.path.join(folder, thumb.name + extn)
    # print("checking whether exists in s3: {}".format(key))
    resp = bucket.get_key(key)
    if not resp:
        # print("does not exist")
        return False
    # print("exists")
    return True


def download_from_s3(img_name):
    local_path = path_for(img_name)
    if not os.path.exists(local_path):
        bucket = get_s3_bucket()
        folder = get_s3_folder()
        k = Key(bucket)
        k.key = os.path.join(folder, img_name)
        k.get_contents_to_filename(local_path)
    return local_path


# -- image details --

def get_width_height(img_path):
    name, extn = os.path.splitext(img_path)
    try:
        o = '0x0'
        if extn in ['.pdf', '.gif']:
            o = check_output('identify -quiet -ping -format "%wx%h" {}[0]'.format(img_path), shell=True)
        elif extn in ['.cdr']:
            wo = check_output('inkscape -z -W {}'.format(img_path), shell=True)
            ho = check_output('inkscape -z -H {}'.format(img_path), shell=True)
            o = "{}x{}".format(int(round(float(wo))), int(round(float(ho))))
        elif extn in ['.psd']:
            # identify command doesn't seem to work on psd files
            # hence using file command and extracting resolution from there
            fo = check_output('file {}'.format(img_path), shell=True)
            possible_size = re.findall(r'\d+\ x\ \d+', fo)
            if len(possible_size) == 1:
                wo, ho = possible_size[0].split(' x ')
                o = "{}x{}".format(int(round(float(wo))), int(round(float(ho))))
        else:
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
    from imgee import storage
    extn = image.extn
    if size and extn in EXTNS:
        if image.no_previews:
            return get_no_previews_url(size)
        img_name = storage.get_resized_image(image, size)
        if not img_name:
            return get_no_previews_url(size)
    else:
        img_name = image.name
    if size and 'thumb_extn' in ALLOWED_MIMETYPES[image.mimetype]:
        extn = ALLOWED_MIMETYPES[image.mimetype]['thumb_extn']
    return get_url(img_name, extn)


def get_thumbnail_url(image):
    return get_image_url(image, app.config.get('THUMBNAIL_SIZE'))
