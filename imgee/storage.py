# -*- coding: utf-8 -*-

import time
import os.path
from subprocess import check_call, CalledProcessError
from glob import glob
import re
import redis
from sqlalchemy import or_
from werkzeug import secure_filename
from datetime import datetime, timedelta

import imgee
from flask import abort
from imgee import app
from imgee.models import db, Thumbnail, StoredFile
from imgee.utils import (newid, guess_extension, get_file_type,
                        path_for, get_s3_folder, get_s3_bucket,
                        download_frm_s3, get_width_height, ALLOWED_MIMETYPES,
                        THUMBNAIL_COMMANDS, exists_in_s3)


# -- functions used in views --

def get_resized_image(img, size, is_thumbnail=False):
    """
    Check if `img` is available with `size` if not make one. Return the name of it.
    """
    registry = imgee.registry
    img_name = img.name
    size_t = parse_size(size)
    if (size_t and size_t[0] != img.width and size_t[1] != img.height) or ('thumb_extn' in ALLOWED_MIMETYPES[img.mimetype] and ALLOWED_MIMETYPES[img.mimetype]['thumb_extn'] != img.extn):
        w_or_h = or_(Thumbnail.width == size_t[0], Thumbnail.height == size_t[1])
        scaled = Thumbnail.query.filter(w_or_h, Thumbnail.stored_file == img).first()
        if scaled and exists_in_s3(scaled):
            print("Found in db")
            img_name = scaled.name
        else:
            print("not in db, resizing")
            size = get_fitting_size((img.width, img.height), size_t)
            resized_filename = get_resized_filename(img, size)
            registry = imgee.registry
            if resized_filename in registry:
                abort(202)
            else:
                registry.add(resized_filename)
            img_name = resize_and_save(img, size, is_thumbnail=is_thumbnail)
            print("done")
            registry.remove(resized_filename)
    return img_name


def save(fp, profile, title=None):
    """
    Attaches the image to the profile and uploads it to S3.
    """
    id_ = newid()
    title = title or secure_filename(fp.filename)
    content_type = get_file_type(fp, fp.filename)
    name, extn = os.path.splitext(fp.filename)
    extn = guess_extension(content_type, extn)
    img_name = "%s%s" % (id_, extn)
    local_path = path_for(img_name)

    with open(local_path, 'w') as img:
        img.write(fp.read())

    stored_file = save_img_in_db(name=id_, title=title, local_path=local_path,
                    profile=profile, mimetype=content_type, orig_extn=extn)
    s3resp = save_on_s3(img_name, content_type=content_type)
    return title, stored_file


# -- actual saving of image/thumbnail and data in the db and on S3.

def save_img_in_db(name, title, local_path, profile, mimetype, orig_extn):
    """
    Save image info in db.
    """
    print(name)
    print(local_path)
    size_in_bytes = os.path.getsize(local_path)
    width, height = get_width_height(local_path)
    stored_file = StoredFile(name=name, title=unicode(title), profile=profile, orig_extn=unicode(orig_extn),
                    size=size_in_bytes, width=width, height=height, mimetype=unicode(mimetype))
    if 'thumb_extn' in ALLOWED_MIMETYPES[mimetype] and ALLOWED_MIMETYPES[mimetype]['thumb_extn'] is False:
        stored_file.no_previews = True
    db.session.add(stored_file)
    db.session.commit()
    return stored_file


def save_tn_in_db(img, tn_name, (tn_w, tn_h)):
    """
    Save thumbnail info in db.
    """
    name, extn = os.path.splitext(tn_name)
    if Thumbnail.query.filter(Thumbnail.name == name).count() == 0:
        tn = Thumbnail(name=name, width=tn_w, height=tn_h, stored_file=img)
        db.session.add(tn)
        db.session.commit()
    return name


def save_on_s3(filename, remotename='', content_type='', bucket='', folder=''):
    """
    Save contents from file named `filename` to `remotename` on S3.
    """
    print("saving on s3: {}".format(filename))
    b = bucket or get_s3_bucket()
    folder = get_s3_folder(folder)

    with open(path_for(filename)) as fp:
        filename = remotename or filename
        k = b.new_key(folder+filename)
        headers = {
            'Cache-Control': 'max-age=31536000',  # 60*60*24*365
            'Content-Type': get_file_type(fp, filename),
            'Expires': datetime.now() + timedelta(days=365)
        }
        k.set_contents_from_file(fp, policy='public-read', headers=headers)
    return filename


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
    """
     Return the size to fit the image to the box
     along the smaller side and preserve aspect ratio.
     w or h being 0 means preserve aspect ratio with that height or width

    >>> get_fitting_size((200, 500), (0, 0))
    [200, 500]
    >>> get_fitting_size((200, 500), (400, 0))
    [400, 1000]
    >>> get_fitting_size((200, 500), (0, 100))
    [40, 100]
    >>> get_fitting_size((200, 500), (50, 50))
    [20, 50]
    >>> get_fitting_size((200, 500), (1000, 400))
    [160, 400]
    >>> get_fitting_size((200, 500), (1000, 1000))
    [400, 1000]
    >>> get_fitting_size((200, 500), (300, 500))
    [200, 500]
    >>> get_fitting_size((200, 500), (400, 600))
    [240, 600]
    """
    if orig_w == 0 or orig_h == 0:
        # this is either a cdr file or a zero width file
        # just go with target  size
        w, h = size
    elif size[0] == 0 and size[1] == 0 and orig_w > 0 and orig_h > 0:
        w, h = orig_w, orig_h
    elif size[0] == 0:
        w, h = orig_w*size[1]/float(orig_h), size[1]
    elif size[1] == 0:
        w, h = size[0], orig_h*size[0]/float(orig_w)
    else:
        w, h = size[0], orig_h*size[0]/float(orig_w)
        if h > size[1]:
            w, h = w*size[1]/float(h), size[1]

    size = int(w), int(h)
    size = map(lambda x: max(x, 1), size)   # let the width or height be atleast 1px.
    return size


def get_resized_filename(img, size):
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
    if 'thumb_extn' in ALLOWED_MIMETYPES[img.mimetype]:
        name = name + ALLOWED_MIMETYPES[img.mimetype]['thumb_extn']
    else:
        name = name + img.extn
    return name


def resize_and_save(img, size, is_thumbnail=False):
    """
    Get the original image from local disk cache, download it from S3 if it misses.
    Resize the image and save resized image on S3 and size details in db.
    """
    src_path = download_frm_s3(img.name + img.extn)
    print("downloaded from s3")

    if 'thumb_extn' in ALLOWED_MIMETYPES[img.mimetype]:
        format = ALLOWED_MIMETYPES[img.mimetype]['thumb_extn']
    else:
        format = img.extn
    format = format.lstrip('.')
    resized_filename = get_resized_filename(img, size)
    if not resize_img(src_path, path_for(resized_filename), size, img.mimetype, format, is_thumbnail=is_thumbnail):
        img.no_previews = True
        db.session.add(img)
        db.session.commit()
        return False

    save_on_s3(resized_filename, content_type=img.mimetype)
    return save_tn_in_db(img, resized_filename, size)


def resize_img(src, dest, size, mimetype, format, is_thumbnail):
    """
    Resize image using ImageMagick.
    `size` is a tuple (width, height)
    resize the image at `src` to the specified `size` and return the path to the resized img.
    """
    if not os.path.exists(src):
        return
    if not size:
        return src

    # get processor value, if none specified, use convert
    processor = ALLOWED_MIMETYPES[mimetype].get('processor', 'convert')
    command = THUMBNAIL_COMMANDS.get(processor)
    prepared_command = command.format(width=size[0], height=size[1], format=format, src=src, dest=dest)
    print(prepared_command)
    try:
        check_call(prepared_command, shell=True)
        return True
    except CalledProcessError as e:
        print(e)
        return False


def clean_local_cache(expiry=24):
    """
    Remove files from local cache which are NOT accessed in the last `expiry` hours.
    """
    cache_path = app.config.get('UPLOADED_FILES_DEST')
    cache_path = os.path.join(cache_path, '*')
    min_atime = time.time() - expiry*60*60

    n = 0
    for f in glob(cache_path):
        if os.path.getatime(f) < min_atime:
            os.remove(f)
            n = n + 1
    return n


def delete(stored_file):
    """
    Delete all the thumbnails and images associated with a file, from local cache and S3.
    Wait for the upload/resize to complete if queued for the same image.
    """
    # remove locally
    cache_path = app.config.get('UPLOADED_FILES_DEST')
    cached_img_path = os.path.join(cache_path, '%s*' % stored_file.name)
    for f in glob(cached_img_path):
        os.remove(f)

    # remove on s3
    extn = stored_file.extn
    # lazy loads don't work - so, no `stored_file.thumbnails`
    thumbnails = Thumbnail.query.filter_by(stored_file=stored_file).all()
    keys = [(get_s3_folder() + thumbnail.name + extn) for thumbnail in thumbnails]
    keys.append(get_s3_folder() + stored_file.name + extn)
    bucket = get_s3_bucket()
    bucket.delete_keys(keys)

    # remove from the db

    # remove thumbnails explicitly.
    # cascade rules don't work as lazy loads don't work in async mode
    Thumbnail.query.filter_by(stored_file=stored_file).delete()
    db.session.delete(stored_file)
    db.session.commit()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
