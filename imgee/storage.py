from os import path
from boto import connect_s3
from boto.s3.key import Key
from imgee import app

def configure():
    """
    Configure the storage backend for the files
    """
    return connect_s3(app.config['AWS_ACCESS_KEY'], app.config['AWS_SECRET_KEY'])

def upload(name, title, connection):
    """
    Upload a file to S3
    """
    bucket = connection.create_bucket(app.config['AWS_BUCKET'])
    k = Key(bucket)
    k.key = name
    k.set_contents_from_filename(path.join(app.config['UPLOADED_FILES_DEST'], title))
