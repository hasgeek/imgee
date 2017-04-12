# -*- coding: utf-8 -*-
#: Site title
SITE_TITLE = 'Imgee'
#: Site id (for network bar)
SITE_ID = 'imgee'
#: Database backend
SQLALCHEMY_DATABASE_URI = 'sqlite:///imgee.db'
#: Secret key
SECRET_KEY = 'make this something random'
#: Timezone
TIMEZONE = 'Asia/Kolkata'
#: LastUser server
LASTUSER_SERVER = ''
#: LastUser client id
LASTUSER_CLIENT_ID = ''
#: LastUser client secret
LASTUSER_CLIENT_SECRET = ''
#: Mail settings
#: MAIL_FAIL_SILENTLY : default True
#: MAIL_SERVER : default 'localhost'
#: MAIL_PORT : default 25
#: MAIL_USE_TLS : default False
#: MAIL_USE_SSL : default False
#: MAIL_USERNAME : default None
#: MAIL_PASSWORD : default None
#: DEFAULT_MAIL_SENDER : default None
MAIL_FAIL_SILENTLY = False
MAIL_SERVER = 'localhost'
DEFAULT_MAIL_SENDER = 'HasGeek <test@example.com>'
MAIL_DEFAULT_SENDER = DEFAULT_MAIL_SENDER
#: Logging: recipients of error emails
ADMINS = []
#: Log file
LOGFILE = 'error.log'
#: File uploads
UPLOADED_FILES_DEST = 'imgee/static/uploads'
#: S3 Configuration
AWS_ACCESS_KEY = 'Set aws access key here'
AWS_SECRET_KEY = 'Set aws secret key here'
AWS_BUCKET = 'set your bucketname here'
AWS_FOLDER = ''     # set this if you want all files to be uploaded to a particular folder eg., 'test/'
#: Domain name for files
MEDIA_DOMAIN = 'http://%s.s3.amazonaws.com' % AWS_BUCKET
THUMBNAIL_SIZE = '75x75'   # WxH in px
UNKNOWN_FILE_THUMBNAIL = 'set name of unknown file thumbnail on media_domain'

REDIS_URL = 'redis://localhost:6379/0'

SERVER_EMAIL = DEFAULT_MAIL_SENDER
EMAIL_HOST = MAIL_SERVER

# ADMINS is list of tuples [(name, addr), ...] rather than a list of email addresses expected by flask-email.
# both formats are supported by SMTPHandler.
ADMINS = [(a.split('@')[0].title(), a) for a in ADMINS]

# EMAIL_HOST_USER = MAIL_USERNAME
# EMAIL_HOST_PASSWORD = MAIL_PASSWORD

#: Path to loading image relative to the root imgee folder
LOADING_IMG = 'imgee/static/img/spinner.gif'
