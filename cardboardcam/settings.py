import tempfile
db_file = tempfile.NamedTemporaryFile()


class Config(object):
    SECRET_KEY = ('o93ryvba8rnyaljrdqp0plaoseryfusihgfjkshfla238uierndq2h3kr'
                  'ha2klmfeps3m4hkgnkjwdh')
    GOOGLE_ANALYTICS_TRACKING_ID = 'UA-882020-14'
    UPLOAD_FOLDER = 'cardboardcam/static/uploads'
    LOG_DIR = 'log/'
    MEDIA_FOLDER = 'static/uploads'
    MEDIA_THUMBNAIL_FOLDER = MEDIA_FOLDER + '/thumbnails'
    MEDIA_URL = '/static/'
    MEDIA_THUMBNAIL_URL = '/static/uploads/thumbnails/'
    THUMBNAIL_MEDIA_ROOT = MEDIA_FOLDER
    THUMBNAIL_MEDIA_THUMBNAIL_ROOT = MEDIA_THUMBNAIL_FOLDER
    THUMBNAIL_MEDIA_THUMBNAIL_URL = MEDIA_THUMBNAIL_URL
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 Mb


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
