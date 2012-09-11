from os import path
from uuid import uuid4
from boto import connect_s3
from boto.s3.bucket import Bucket
from boto.s3.key import Key
from PIL import Image
from imgee import app
from imgee.models import db


IMAGES = list('jpg jpe jpeg png gif svg bmp'.split())


def upload(name, title):
    """
    Upload a file to S3
    """
    conn = connect_s3(app.config['AWS_ACCESS_KEY'], app.config['AWS_SECRET_KEY'])
    bucket = Bucket(conn, app.config['AWS_BUCKET'])
    k = Key(bucket)
    k.key = name
    k.set_contents_from_filename(path.join(app.config['UPLOADED_FILES_DEST'], title))


def is_image(filename):
    """
    Check if a given filename is an image or not
    """
    extension = filename.rsplit('.', 1)[-1]
    if extension in IMAGES:
        return True
    return False


def create_thumbnail(stored_file, size):
    """
    Create a thumbnail for a given file and given size
    """
    thumbnail = Thumbnail(name=uuid4().hex, size=size, stored_file=stored_file)
    db.session.add(thumbnail)
    db.session.commit()
    conn = connect_s3(app.config['AWS_ACCESS_KEY'], app.config['AWS_SECRET_KEY'])
    bucket = Bucket(conn, app.config['AWS_BUCKET'])
    thumbnail_path = path.join(app.config['UPLOADED_FILES_DEST'], thumbnail.name)
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


def convert_size(size):
    converted = size.split('x')
    if len(converted) != 2:
        return None
    for k, v in enumerate(converted):
        if v.isdigit():
            converted[k] = int(v)
        else:
            return None
    return converted
