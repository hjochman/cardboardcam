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
env = os.environ.get('DEPLOYMENT', 'prod')
app = create_app(getattr(settings, '%sConfig' % env.capitalize()),
                 env=env)

if __name__ == "__main__":
    app.run()
