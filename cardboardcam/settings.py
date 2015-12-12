import tempfile
db_file = tempfile.NamedTemporaryFile()


class Config(object):
    SECRET_KEY = ('o93ryvba8rnyaljrdqp0plaoseryfusihgfjkshfla238uierndq2h3kr'
                  'ha2klmfeps3m4hkgnkjwdh')
    GOOGLE_ANALYTICS_TRACKING_ID = 'UA-882020-14'
    UPLOAD_FOLDER = 'cardboardcam/static/uploads'
    LOG_DIR = 'log/'
    MEDIA_FOLDER = UPLOAD_FOLDER
    MEDIA_THUMBNAIL_FOLDER = MEDIA_FOLDER + '/thumbnails'
    MEDIA_URL = '/static/'
    MEDIA_THUMBNAIL_URL = '/static/uploads/thumbnails/'
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 Mb


class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../database.db'

    CACHE_TYPE = 'simple'
    APP_BASE = '/srv/webapps/cardboardcam/src/'
    UPLOAD_FOLDER = APP_BASE + 'cardboardcam/static/uploads'

    MEDIA_FOLDER = UPLOAD_FOLDER
    MEDIA_THUMBNAIL_FOLDER = MEDIA_FOLDER + '/thumbnails'


class DevConfig(Config):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_DATABASE_URI = 'sqlite:///../database.db'

    CACHE_TYPE = 'null'
    ASSETS_DEBUG = True


class TestConfig(Config):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + db_file.name
    SQLALCHEMY_ECHO = True

    CACHE_TYPE = 'null'
    WTF_CSRF_ENABLED = False
