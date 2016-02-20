#!/usr/bin/env python3
import sys
import os

# Active your Virtual Environment, which I'm assuming you've already setup
# activate_this='/home/perry/.virtualenvs/cardboardcam/bin/activate_this.py'
# exec(open(activate_this).read(), dict(__file__=activate_this))

# Appending our Flask project files
# sys.path.append('/home/perry/webapps/cardboard')

# Launching our app
from cardboardcam import create_app, settings

# env = 'dev'

# we can choose DevConfig vs ProdConfig settings classes using the
# environment variable ENV
env = os.environ.get('ENV', 'prod')
config = getattr(settings, '%sConfig' % env.capitalize())

# alternatively, we can source all our config variables directly from the
# shell environment (12-factor style)
# config = os.environ

app = create_app(config,
                 env=env)

if __name__ == "__main__":
    app.run()
