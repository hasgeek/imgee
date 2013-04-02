import os.path
from uuid import uuid4
import re
from PIL import Image
import mimetypes
from StringIO import StringIO

from boto import connect_s3
from boto.s3.bucket import Bucket
from boto.s3.key import Key

from imgee import app
from imgee.models import db, Thumbnail

def get_s3_bucket():
    conn = connect_s3(app.config['AWS_ACCESS_KEY'], app.config['AWS_SECRET_KEY'])
    bucket = Bucket(conn, app.config['AWS_BUCKET'])
    return bucket

def save(fp, img_name, remote=True, content_type=None):
    local_path =  os.path.join(app.config['UPLOADED_FILES_DEST'], img_name)
    with open(local_path, 'w') as img:
        img.write(fp.read())

    if remote:
        fp.seek(0)
        save_on_s3(fp, img_name, content_type=content_type)

def get_file_type(filename):
    return mimetypes.guess_type(filename)[0]

def save_on_s3(fp, filename, content_type=''):
    b = get_s3_bucket()
    k = b.new_key(filename)
    content_type = content_type or get_file_type(filename)
    headers = {
        'Cache-Control': 'max-age=31536000',    #60*60*24*365
        'Content-Type': content_type,
    }
    k.set_contents_from_file(fp, policy='public-read', headers=headers)

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
            img_name = resize_and_save(img, size)
    return img_name

def get_image_locally(img_name):
    local_path =  path_for(img_name)
    if not os.path.exists(local_path):
        bucket = get_s3_bucket()
        k = Key(bucket)
        k.key = img_name
        k.get_contents_to_filename(local_path)
    return local_path

def resize_and_save(img, size):
    src_path =  get_image_locally(img.name)
    scaled_img_name = uuid4().hex
    content_type = get_file_type(img.title) # eg: image/jpeg
    format = content_type.split('/')[1] if content_type else None
    scaled = resize_img(src_path, size, format)
    save_on_s3(scaled, scaled_img_name, content_type)

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

def resize_img(src, size, format):
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
    imgio = StringIO()
    resized.save(imgio, format=format, quality=100)
    imgio.seek(0)
    return imgio

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
