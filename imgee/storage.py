import os.path
from uuid import uuid4
import re
from PIL import Image
import mimetypes
from StringIO import StringIO

from boto import connect_s3
from boto.s3.bucket import Bucket
from boto.s3.key import Key

from flask.ext.uploads import save as uploads_save

from imgee import app
from imgee.models import db, Thumbnail

def get_s3_bucket():
    conn = connect_s3(app.config['AWS_ACCESS_KEY'], app.config['AWS_SECRET_KEY'])
    bucket = Bucket(conn, app.config['AWS_BUCKET'])
    return bucket

def save(fp, img_name, remote=True):
    local_path =  os.path.join(app.config['UPLOADED_FILES_DEST'], img_name)
    with open(local_path, 'w') as img:
        img.write(fp.read())

    if remote:
        fp.seek(0)
        uploads_save(fp, img_name)

def path_for(img_name):
    return os.path.join(app.config['UPLOADED_FILES_DEST'], img_name)

def get_image_name(img, size):
    img_name = img.name
    size_t = split_size(size)
    if size_t:
        scaled = Thumbnail.query.filter_by(size=size, stored_file=img).first()
        if scaled:
            img_name = scaled.name
        else:
            img_name = resize_and_save(img, size, format)
    return img_name

def get_image_locally(img_name):
    local_path =  path_for(img_name)
    if not os.path.exists(local_path):
        bucket = get_s3_bucket()
        k = Key(bucket)
        k.key = img_name
        k.get_contents_to_filename(local_path)
    return local_path

def resize_and_save(img, size, format):
    format = os.path.splitext(img.title)[1].lstrip('.')
    src_path =  get_image_locally(img.name)
    scaled_img_name = uuid4().hex
    scaled_path = path_for(scaled_img_name)
    resize_img(src_path, scaled_path, size, format)
    scaled = Thumbnail(name=scaled_img_name, size=size, stored_file=img)
    db.session.add(scaled)
    db.session.commit()
    return scaled_img_name

def get_size((orig_w, orig_h), (w, h)):
    # return size which preserves the aspect ratio of the original image.
    # w or h being None means square size
    if w != 0:
        size = (w, orig_h*w/orig_w)
    elif w == None:
        size = (h, h)
    elif h == None:
        size = (w, w)
    else:
        size = (orig_w*h/orig_h, h)
    return size

def resize_img(src, dest, size, format):
    """
    `size` is a tuple (width, height) or a string '<width>x<height>'.
    resize the image at `path` to the specified `size` and return the resized img.
    """
    if isinstance(size, (str, unicode)):
        size = split_size(size)

    if (not size) or (not os.path.exists(src)):
        return
    img = Image.open(src)
    img.load()
    size = get_size(img.size, size)
    resized = img.resize(size, Image.ANTIALIAS)
    resized.save(dest, format=format, quality=100)

def split_size(size):
    """ return (w, h) if size is 'wxh'
    """
    r= r'^(\d+)(x(\d+))?$'
    matched = re.match(r, size)
    if matched:
        w, h = matched.group(1, 2)
        h = int(h.lstrip('x')) if h != None else None
        return int(w), h

def delete_image(stored_file):
    """
    Delete all the thumbnails and images associated with a file
    """
    keys = [thumbnail.name for thumbnail in stored_file.thumbnails]
    keys.append(stored_file.name)
    bucket = get_s3_bucket()
    bucket.delete_keys(keys)
