import sys

# Active your Virtual Environment, which I'm assuming you've already setup
# activate_this='/home/perry/.virtualenvs/cardboardcam/bin/activate_this.py'
# exec(open(activate_this).read(), dict(__file__=activate_this))

# Appending our Flask project files
# sys.path.append('/home/perry/webapps/cardboard')

# Launching our app
from cardboardcam import create_app, settings

config = settings.ProdConfig
# config = settings.DevConfig
application = create_app(config)

if __name__ == "__main__":
    application.run()

#def application(environ, start_response):
#    output = 'Welcome to your mod_wsgi website! It uses:\n\nPython %s' % sys.version
#    output += '\nWSGI version: %s' % str(environ['mod_wsgi.version'])
#
#    response_headers = [
#        ('Content-Length', str(len(output))),
#        ('Content-Type', 'text/plain'),
#    ]
#
#    start_response('200 OK', response_headers)
#
#    return [bytes(output, 'utf-8')]
