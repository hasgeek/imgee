# -*- coding: utf-8 -*-
from os import environ

# this will sit inside `app.static_folder`
UPLOADED_FILES_DIR = 'test_uploads'

AWS_FOLDER = 'test/'

UNKNOWN_FILE_THUMBNAIL = 'unknown.jpeg'

#: S3 Configuration; AWS credentials with restricted access
AWS_ACCESS_KEY = environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = environ.get('AWS_SECRET_KEY')
AWS_BUCKET = environ.get('AWS_BUCKET', 'imgee-testing')
AWS_FOLDER = 'test'

MEDIA_DOMAIN = 'https://%s.s3.amazonaws.com' % AWS_BUCKET

SQLALCHEMY_DATABASE_URI = 'sqlite://'
WTF_CSRF_ENABLED = False

THUMBNAIL_SIZE = '75x75'
