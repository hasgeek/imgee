from os import environ

# this will sit inside `app.static_folder`
UPLOADED_FILES_DIR = 'test_uploads'

AWS_FOLDER = 'test/'

UNKNOWN_FILE_THUMBNAIL = 'unknown.jpeg'

#: S3 Configuration; AWS credentials with restricted access
#: S3 Configuration
AWS_ACCESS_KEY = 'AKIAIRIRVOH3RE5SKR4A'
AWS_SECRET_KEY = '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'
AWS_BUCKET = 'imgee'
AWS_FOLDER = 'test'
MEDIA_DOMAIN = 'http://%s.s3.amazonaws.com/' % AWS_BUCKET

SQLALCHEMY_DATABASE_URI = 'sqlite://'
WTF_CSRF_ENABLED = False

THUMBNAIL_SIZE = '75x75'
