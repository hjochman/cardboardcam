from uuid import uuid4
import os
import tempfile

db_file = tempfile.NamedTemporaryFile()


class Config(object):
    # You should change this to your own string
    SECRET_KEY = uuid4().get_hex()
    GOOGLE_ANALYTICS_TRACKING_ID = ""
    UPLOAD_FOLDER = "cardboardcam/static/uploads"
    LOG_DIR = "logs/"
    MEDIA_FOLDER = UPLOAD_FOLDER
    MEDIA_THUMBNAIL_FOLDER = os.path.join(MEDIA_FOLDER, "thumbnails")
    MEDIA_URL = "/static/"
    MEDIA_THUMBNAIL_URL = "/static/uploads/thumbnails/"
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 Mb


class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///../database.db"

    CACHE_TYPE = "simple"


class DevConfig(Config):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_DATABASE_URI = "sqlite:///../database.db"

    CACHE_TYPE = "null"
    ASSETS_DEBUG = True


class TestConfig(Config):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + db_file.name
    SQLALCHEMY_ECHO = True

    CACHE_TYPE = "null"
    WTF_CSRF_ENABLED = False
