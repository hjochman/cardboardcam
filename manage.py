#!/usr/bin/env python3

import os

from flask_script import Manager, Server
from flask_script.commands import ShowUrls, Clean
from flask_assets import ManageAssets
from cardboardcam import assets_env
from cardboardcam import create_app
from cardboardcam.models import db, User

# default to dev config because no one should use this in
# production anyway
env = os.environ.get("APPNAME_ENV", "dev")
app = create_app("cardboardcam.settings.%sConfig" % env.capitalize(), env=env)

manager = Manager(app)
manager.add_command("assets", ManageAssets(assets_env))
manager.add_command("server", Server())
manager.add_command("show-urls", ShowUrls())
manager.add_command("clean", Clean())


@manager.shell
def make_shell_context():
    """ Creates a python REPL with several default imports
        in the context of the app
    """

    return dict(app=app, db=db, User=User)


@manager.command
def createdb():
    """ Creates a database with all of the tables defined in
        your SQLAlchemy models
    """

    db.create_all()


if __name__ == "__main__":
    manager.run()
