from flask.ext.cache import Cache
from flask.ext.debugtoolbar import DebugToolbarExtension
from flask.ext.login import LoginManager
from flask_assets import Environment
from flask_wtf.csrf import CsrfProtect
from flask.ext.thumbnails import Thumbnail
from flask.ext.rq import RQ

# from flask_aiohttp import AioHTTP

from cardboardcam.models import User

# Setup flask cache
cache = Cache()

# init flask assets
assets_env = Environment()

debug_toolbar = DebugToolbarExtension()

login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message_category = "warning"

csrf = CsrfProtect()

thumbnail = Thumbnail()

rq = RQ()

# aio = AioHTTP()

@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)
