from os import path
from boto import connect_s3
from boto.s3.bucket import Bucket
from boto.s3.key import Key
from imgee import app


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
