import os.path
from uuid import uuid4
import re
from boto import connect_s3
from boto.s3.bucket import Bucket
from boto.s3.key import Key
from PIL import Image
from imgee import app
from imgee.models import db, Thumbnail



IMAGES = 'jpg jpe jpeg png gif svg bmp'.split()

def get_s3_bucket():
    conn = connect_s3(app.config['AWS_ACCESS_KEY'], app.config['AWS_SECRET_KEY'])
    bucket = Bucket(conn, app.config['AWS_BUCKET'])
    return bucket

def is_image(filename):
    """
    Check if a given filename is an image or not
    """
    extension = filename.rsplit('.', 1)[-1]
    return extension in IMAGES


def create_thumbnail(stored_file, size):
    """
    Create a thumbnail for a given file and given size
    """
    thumbnail = Thumbnail(name=uuid4().hex, size=size, stored_file=stored_file)
    db.session.add(thumbnail)
    db.session.commit()
    thumbnail_path = os.path.join(app.config['UPLOADED_FILES_DEST'], thumbnail.name)
    bucket = get_s3_bucket()
    k = Key(bucket)
    k.key = stored_file.name
    k.get_contents_to_filename(thumbnail_path)
    try:
        img = Image.open(thumbnail_path)
        img.load()
        img.thumbnail(size, Image.ANTIALIAS)
        img.save(thumbnail_path)
    except IOError:
        return None
    return thumbnail.name


def split_size(size):
    """ return (a, b) if size is 'axb'
    """
    r = r'^(\d+)x(\d+)$'
    matched = re.match(r, size)
    if matched:
        a, b = matched.group(1, 2)
        return int(a), int(b)

def delete_image(stored_file):
    """
    Delete all the thumbnails and images associated with a file
    """
    keys = [thumbnail.name for thumbnail in stored_file.thumbnails]
    keys.append(stored_file.name)
    bucket = get_s3_bucket()
    bucket.delete_keys(keys)
