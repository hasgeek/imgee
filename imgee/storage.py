# -*- coding: utf-8 -*-

import os.path
import re
import mimetypes
from StringIO import StringIO
from PIL import Image

from boto import connect_s3
from boto.s3.bucket import Bucket
from boto.s3.key import Key

from imgee import app
from imgee.models import db, Thumbnail
from imgee.utils import newid, ImageQueue

s3uploadqueue = ImageQueue()

def get_s3_bucket():
    conn = connect_s3(app.config['AWS_ACCESS_KEY'], app.config['AWS_SECRET_KEY'])
    bucket = Bucket(conn, app.config['AWS_BUCKET'])
    return bucket


def save(fp, img_name, remote=True, content_type=None):
    img_name = "%s%s" % (img_name, os.path.splitext(fp.filename)[1])
    local_path = os.path.join(app.config['UPLOADED_FILES_DEST'], img_name)
    with open(local_path, 'w') as img:
        img.write(fp.read())

    if remote:
        s3uploadqueue.add(img_name)


def get_file_type(filename):
    return mimetypes.guess_type(filename)[0]


def get_s3_folder(f=''):
    f = f or app.config['AWS_FOLDER']
    if f and not f.endswith('/'):
        f = f + '/'
    return f or ''


def save_on_s3(fp, filename='', content_type='', folder=''):
    b = get_s3_bucket()
    filename = filename or fp.name
    folder = get_s3_folder(folder)
    k = b.new_key(folder+filename)
    content_type = content_type or get_file_type(filename)
    headers = {
        'Cache-Control': 'max-age=31536000',  # 60*60*24*365
        'Content-Type': content_type,
    }
    k.set_contents_from_file(fp, policy='public-read', headers=headers)


def path_for(img_name):
    return os.path.join(app.config['UPLOADED_FILES_DEST'], img_name)


def get_resized_image(img, size, thumbnail=False):
    img_name = img.name
    if isinstance(size, (str, unicode)):
        size_t = split_size(size)
    elif isinstance(size, tuple):
        size_t, size = size, "%sx%s" % size
    if size_t:
        scaled = Thumbnail.query.filter_by(size=size, stored_file=img).first()
        if scaled:
            img_name = scaled.name
        else:
            img_name = resize_and_save(img, size_t, thumbnail=thumbnail)
    return img_name


def get_image_locally(img_name):
    local_path = path_for(img_name)
    if not os.path.exists(local_path):
        bucket = get_s3_bucket()
        k = Key(bucket)
        k.key = img_name
        k.get_contents_to_filename(local_path)
    return local_path


def resize_and_save(img, size, thumbnail=False):
    extn = os.path.splitext(img.title)[1]
    src_path = get_image_locally(img.name+extn)
    scaled_img_name = newid()
    content_type = get_file_type(img.title)  # eg: image/jpeg
    format = content_type.split('/')[1] if content_type else None
    scaled = resize_img(src_path, size, format, thumbnail=thumbnail)
    save_on_s3(scaled, scaled_img_name+extn, content_type)

    size_s = "%sx%s" % size
    scaled = Thumbnail(name=scaled_img_name, size=size_s, stored_file=img)
    db.session.add(scaled)
    db.session.commit()
    return scaled_img_name


def get_size((orig_w, orig_h), (w, h)):
    # fit the image to the box along the smaller side and preserve aspect ratio.
    # w or h being 0 means preserve aspect ratio with that height or width

    if (h == 0) or (orig_w <= orig_h):
        size = (w, w*orig_h/orig_w)
    else:
        size = (h*orig_w/orig_h, h)

    size = map(lambda x: max(x, 1), size)   # let the width or height be atleast 1px.
    return map(int, size)


def resize_img(src, size, format, thumbnail):
    """
    `size` is a tuple (width, height)
    resize the image at `src` to the specified `size` and return the resized img.
    """
    if (not size) or (not os.path.exists(src)):
        return
    img = Image.open(src)
    img.load()

    size = get_size(img.size, size)
    resized = img.resize(size, Image.ANTIALIAS)

    if thumbnail:
        # and crop the rest, keeping the center.
        w, h = resized.size
        tw, th = app.config.get('THUMBNAIL_SIZE')
        left, top = int((w-tw)/2), int((h-th)/2)
        resized = resized.crop((left, top, left+tw, top+th))

    imgio = StringIO()
    resized.save(imgio, format=format, quality=100)
    imgio.seek(0)
    return imgio


def split_size(size):
    """ return (w, h) if size is 'wxh'
    """
    r = r'^(\d+)(x(\d+))?$'
    matched = re.match(r, size)
    if matched:
        w, h = matched.group(1, 2)
        h = int(h.lstrip('x')) if h is not None else 0
        return int(w), h


def delete_on_s3(stored_file):
    """
    Delete all the thumbnails and images associated with a file
    """
    keys = [get_s3_folder()+thumbnail.name for thumbnail in stored_file.thumbnails]
    keys.append(get_s3_folder()+stored_file.name)
    bucket = get_s3_bucket()
    bucket.delete_keys(keys)
