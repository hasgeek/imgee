import os

UPLOADED_FILES_DEST = 'imgee/static/test_uploads'
AWS_FOLDER = 'test/'

UNKNOWN_FILE_THUMBNAIL = 'unknown.jpeg'

#: S3 Configuration; AWS credentials with restricted access
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY', '')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY', '')
AWS_BUCKET = os.getenv('AWS_BUCKET', 'imgee')
AWS_FOLDER = 'test'

MEDIA_DOMAIN = 'https://%s.s3.amazonaws.com' % AWS_BUCKET

SQLALCHEMY_DATABASE_URI = 'sqlite:///imgee.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

SERVER_NAME = 'imgee.local:4500'
