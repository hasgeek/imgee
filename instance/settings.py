# -*- coding: utf-8 -*-
#: Site title
SITE_TITLE = 'Imgee'
#: Site id (for network bar)
SITE_ID = ''
#: Database backend
SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
#: Secret key
SECRET_KEY = 'make this something random'
#: Timezone
TIMEZONE = 'Asia/Calcutta'
#: LastUser server
LASTUSER_SERVER = 'https://login.hasgeek.com/'
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
DEFAULT_MAIL_SENDER = ('HasGeek', 'test@example.com')
#: Logging: recipients of error emails
ADMINS = []
#: Log file
LOGFILE = 'error.log'
#: File uploads
UPLOADED_FILES_DEST = 'imgee/static/uploads'
#: S3 Configuration
AWS_ACCESS_KEY = 'Set aws access key here'
AWS_SECRET_KEY = 'Set aws secret key here'
AWS_BUCKET = 'media.hasgeek.com'
