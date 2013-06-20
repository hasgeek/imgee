from os import environ
UPLOADED_FILES_DEST = 'imgee/static/test_uploads'
AWS_FOLDER = 'test/'

UNKNOWN_FILE_THUMBNAIL = 'unknown.jpeg'

#: S3 Configuration
AWS_ACCESS_KEY = 'AKIAINHIM7Q7GGWGDTVA'
AWS_SECRET_KEY = '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'
AWS_BUCKET = 'media.hasgeek.com'
AWS_FOLDER = 'test/'     # set this if you want all files to be uploaded to a particular folder eg., 'test/'
#: Domain name for files
MEDIA_DOMAIN = 'http://media.hasgeek.com/'

SQLALCHEMY_DATABASE_URI = 'sqlite://test.db'
CSRF_ENABLED = False

# redis settings for RQ
RQ_DEFAULT_URL = "set it here" # set some non empty string here so that the default url is not set.
