# Cardboard Camera Toolkit

A webapp for splitting/joining photos from Cardboard Camera to/from a stereo pair and audio file.

Available here: http://cctoolkit.vectorcult.com/

## Installation and setup

The server will run on Linux, OS X and probably other Unix-like systems.

```
git clone https://bitbucket.org/pansapiens/cardboardcam.git
cd cardboardcam
```

Create a virtualenv and install dependencies:

```
sudo apt-get install libexempi3  # (Ubuntu/Debian)
brew install exempi              # (Homebrew on OS X)
mkvirtualenv ~/.virtualenvs/cardboardcam
pip install -U -r requirements.txt
```

Edit `cardboardcam/settings.py`, specifically changing `SECRET_KEY`, `GOOGLE_ANALYTICS_TRACKING_ID` and if running in production, `APP_BASE`.

## Running the server

Run the server in development mode accessible only from localhost using:

```
python3 manage.py runserver
```

Or, in development mode accessible from any host (not recommended if this port is publicly accessible):
```
python3 manage.py runserver -h 0.0.0.0
```

Or, to run the server in production mode (usually proxied behind nginx):
```
ENV=prod python3 wsgi.py
```

You can connect to the running server at: http://127.0.0.1:5000/ 

## Development notes

Most of the main business logic is in `cardboardcam/controllers/main.py` and `cardboardcam/static/js/main.js`.

When running in production, Javascript and CSS is bundled and minified upon startup, as defined in `cardboardcam/assets.py`.
If you modifiy the Javascript or CSS in production the server must be restarted to re-bundle.

## Acknowledgements

Initial Flask app template from: 
[https://jackstouffer.github.io/Flask-Foundation/](https://jackstouffer.github.io/Flask-Foundation/)

_"Man with Axe with Cardboard"_ image modified by [/u/Zombieist](https://www.reddit.com/u/Zombieist), based on a Public Domain image.

## License

BSD. See LICENSE.md
