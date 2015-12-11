from uuid import uuid4

import tempfile
db_file = tempfile.NamedTemporaryFile()


class Config(object):
    # You should change this to your own string
    SECRET_KEY = uuid4().get_hex()
    UPLOAD_FOLDER = 'cardboardcam/static/uploads'
    LOG_DIR = 'log/'
    MEDIA_FOLDER = UPLOAD_FOLDER
    MEDIA_THUMBNAIL_FOLDER = MEDIA_FOLDER + '/thumbnails'
    MEDIA_URL = '/static/'
    MEDIA_THUMBNAIL_URL = '/static/uploads/thumbnails/'
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 Mb

    # Redis server/database for the default queue
    RQ_DEFAULT_URL = 'redis://localhost:6379/0'
    # RQ_DEFAULT_PASSWORD = 'pa9Ma0fie7bi6utheidachohZaigi4shaey9aepe3oesaepic7choh6Eiph8Shab'
    # Redis server/database for the 'low' and 'high' queues
    # RQ_LOW_URL = 'redis://localhost:6379/1'
    # RQ_HIGH_URL = 'redis://localhost:6379/2'


class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../database.db'

    CACHE_TYPE = 'simple'

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
