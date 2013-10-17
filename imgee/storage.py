# -*- coding: utf-8 -*-

import time
import os.path
from glob import glob
import re
import mimetypes
from StringIO import StringIO
from PIL import Image

from imgee import app, celery
from imgee.models import db, Thumbnail, StoredFile
from imgee.async import queueit
from imgee.utils import (newid, guess_extension, get_file_type,
                        path_for, get_s3_folder, get_s3_bucket,
                        download_frm_s3, get_width_height)


# -- functions used in views --

def get_resized_image(img, size, is_thumbnail=False):
    """
    Check if `img` is available with `size` if not make a one. Return the name of it.
    """
    img_name = img.name
    size_t = parse_size(size)
    if size_t and size_t[0] != img.width and size_t[1] != img.height:
        size = '%sx%s' % size_t
        scaled = Thumbnail.query.filter_by(size=size, stored_file=img).first()
        if scaled:
            img_name = scaled.name
        else:
            resized_name = '%s%s' % (get_resized_name(img, size_t), img.extn)
            job = queueit('resize_and_save', img, size_t, is_thumbnail=is_thumbnail, taskid=resized_name)
            return job
    return img_name


def save(fp, profile, img_name=None):
    """
    Attaches the image to the profile and uploads it to S3.
    """
    id_ = img_name or newid()
    content_type = get_file_type(fp.filename)
    img_name = "%s%s" % (id_, guess_extension(content_type))
    local_path = path_for(img_name)

    with open(local_path, 'w') as img:
        img.write(fp.read())

    save_img_in_db(name=id_, title=fp.filename, local_path=local_path,
                    profile=profile, mimetype=content_type)
    job = queueit('save_on_s3', img_name, content_type=content_type, taskid=img_name)
    return job


# -- actual saving of image/thumbnail and data in the db and on S3.

def save_img_in_db(name, title, local_path, profile, mimetype):
    """
    Save image info in db.
    """
    size_in_bytes = os.path.getsize(local_path)
    width, height = get_width_height(local_path)
    stored_file = StoredFile(name=name, title=title, profile=profile,
                    size=size_in_bytes, width=width, height=height, mimetype=mimetype)
    db.session.add(stored_file)
    db.session.commit()


def save_tn_in_db(img, tn_name, size_t):
    """
    Save thumbnail info in db.
    """
    name, extn = os.path.splitext(tn_name)
    size_s = "%sx%s" % size_t
    tn = Thumbnail(name=name, size=size_s, stored_file=img)
    db.session.add(tn)
    db.session.commit()
    return name


@celery.task(name='imgee.storage.s3-upload')
def save_on_s3(filename, remotename='', content_type='', bucket='', folder=''):
    """
    Save contents from file named `filename` to `remotename` on S3.
    """
    filepath = path_for(filename)
    b = bucket or get_s3_bucket()
    folder = get_s3_folder(folder)

    with open(filepath) as fp:
        filename = remotename or filename
        k = b.new_key(folder+filename)
        content_type = content_type or get_file_type(filename)
        headers = {
            'Cache-Control': 'max-age=31536000',  # 60*60*24*365
            'Content-Type': content_type,
        }
        k.set_contents_from_file(fp, policy='public-read', headers=headers)
    return remotename



# -- size calculations --

def parse_size(size):
    """
    Calculate and return (w, h) from the query parameter `size`.
    Returns None if not formattable.
    """
    if isinstance(size, (str, unicode)):
        # return (w, h) if size is 'wxh'
        r = r'^(\d+)(x(\d+))?$'
        matched = re.match(r, size)
        if matched:
            w, h = matched.group(1, 2)
            h = int(h.lstrip('x')) if h is not None else 0
            return int(w), h
    elif isinstance(size, (tuple, list)) and len(size) == 2:
        return tuple(map(int, size))


def get_fitting_size((orig_w, orig_h), size):
    # return the size to fit the image to the box
    # along the smaller side and preserve aspect ratio.
    # w or h being 0 means preserve aspect ratio with that height or width

    size = size[0] or orig_w, size[1] or orig_h
    w, h = orig_w, orig_h

    w, h = size[0], h*size[0]/float(w)
    if h > size[1]:
        w, h = w*size[1]/float(h), size[1]

    size = int(w), int(h)
    size = map(lambda x: max(x, 1), size)   # let the width or height be atleast 1px.
    return size


def get_resized_name(img, size):
    """
    Return a name for the resized image.
    """
    w, h = size
    if w and h:
        name = '%s_w%s_h%s' % (img.name, w, h)
    elif w:
        name = '%s_w%s' % (img.name, w)
    elif h:
        name = '%s_h%s' % (img.name, h)
    else:
        name = img.name
    return name


@celery.task(name='imgee.storage.resize-and-s3-upload')
def resize_and_save(img, size, is_thumbnail=False):
    """ Get the original image from local disk cache, download it from S3 if it misses.
    Resize the image and save resized image on S3 and size details in db.
    """
    src_path = download_frm_s3(img.name + img.extn)

    format = guess_extension(img.mimetype).lstrip('.')
    resized_name = '%s%s' % (get_resized_name(img, size), img.extn)
    resize_img(src_path, path_for(resized_name), size, format, is_thumbnail=is_thumbnail)

    save_on_s3(resized_name, content_type=img.mimetype)
    return save_tn_in_db(img, resized_name, size)


def resize_img(src, dest, size, format, is_thumbnail):
    """
    Resize image using PIL.
    `size` is a tuple (width, height)
    resize the image at `src` to the specified `size` and return the path to the resized img.
    """
    if not os.path.exists(src):
        return
    if not size:
        return src

    img = Image.open(src)
    img.load()

    size = get_fitting_size(img.size, size)
    resized = img.resize(size, Image.ANTIALIAS)

    if is_thumbnail:
        # and crop the rest, keeping the center.
        w, h = resized.size
        tw, th = map(int, app.config.get('THUMBNAIL_SIZE').split('x'))
        left, top = int((w-tw)/2), int((h-th)/2)
        resized = resized.crop((left, top, left+tw, top+th))

    resized.save(dest, format=format, quality=100)


def clean_local_cache(expiry=24):
    """
    Remove files from local cache which are NOT accessed in the last `expiry` hours.
    """
    cache_path = app.config.get('UPLOADED_FILES_DEST')
    cache_path = os.path.join(cache_path, '*')
    min_atime = time.time() - expiry*60*60

    n = 0
    for f in glob(cache_path):
        print os.path.getatime(f), min_atime
        if os.path.getatime(f) < min_atime:
            os.remove(f)
            n = n + 1
    return n


def delete_on_s3(stored_file):
    """
    Delete all the thumbnails and images associated with a file
    """
    extn = stored_file.extn
    keys = [(get_s3_folder() + thumbnail.name + extn) for thumbnail in stored_file.thumbnails]
    keys.append(get_s3_folder() + stored_file.name + extn)
    bucket = get_s3_bucket()
    bucket.delete_keys(keys)
