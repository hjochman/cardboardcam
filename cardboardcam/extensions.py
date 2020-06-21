# from flask_cache import Cache
from flask_caching import Cache

from flask_login import LoginManager
from flask_assets import Environment

# from flask_wtf.csrf import CsrfProtect
from flask_thumbnails import Thumbnail

from cardboardcam.models import User

# Setup flask cache
cache = Cache()

# init flask assets
assets_env = Environment()

login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message_category = "warning"

# csrf = CsrfProtect()

thumbnail = Thumbnail()


@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)
