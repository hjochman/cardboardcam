from os import path
from urllib.parse import urljoin
from flask import Blueprint, render_template, flash, request, redirect, url_for, abort
from flask import current_app
from flask.ext.login import login_user, logout_user, login_required

from werkzeug import secure_filename

from cardboardcam.extensions import cache
from cardboardcam.forms import LoginForm, ImageForm
from cardboardcam.models import User

from base64 import b64decode
from libxmp.utils import file_to_dict

main = Blueprint('main', __name__)

# upload_folder = 'uploads'
#
# @main.record
# def record_auth(setup_state):
#     global upload_folder
#     upload_folder = setup_state.app.config.get('UPLOAD_FOLDER')

def upload_dir():
    return current_app.config.get('UPLOAD_FOLDER', '/tmp')

@main.route('/', methods=['GET', 'POST'])
@cache.cached(timeout=1000)
def home():
    form = ImageForm()
    filename = None
    return render_template('index.html', form=form, filename=filename)

@main.route('/upload', methods=['POST'])
def upload():
    form = ImageForm()

    if form.validate_on_submit():
        filename = secure_filename(form.image.data.filename)
        img_path = path.join(upload_dir(), filename)
        form.image.data.save(img_path)
        try:
            split_vr_image(img_path)
        except:
            abort(500);

        return redirect(url_for('main.result', img_filename=filename))
    else:
        filename = None
        return render_template('index.html', form=form, filename=filename)

@main.route('/<img_filename>', methods=['GET'])
def result(img_filename=None):
    upload_folder = upload_dir()
    input_file = path.join(upload_folder, img_filename)
    second_image = path.join(upload_folder, get_second_image_name(img_filename))
    audio_file = path.join(upload_folder, get_audio_file_name(img_filename))
    if path.isfile(input_file) and path.isfile(second_image) and path.isfile(audio_file):
        pass
    else:
        abort(404)

    input_file_url = url_for('static', filename='uploads/' + img_filename)
    second_image_url = url_for('static', filename='uploads/' + get_second_image_name(img_filename))
    audio_file_url = url_for('static', filename='uploads/' + get_audio_file_name(img_filename))
    return render_template('result.html',
                           input_filename=input_file_url,
                           second_image=second_image_url,
                           audio_filename=audio_file_url)

def get_second_image_name(img_filename):
    return path.splitext(img_filename)[0] + "_righteye.jpg"

def get_audio_file_name(img_filename):
    return path.splitext(img_filename)[0] + "_audio.mp4"

def split_vr_image(img_filename):
    xmp = file_to_dict(img_filename)

    audio_b64 = xmp[u'http://ns.google.com/photos/1.0/audio/'][1][1]

    afh = open(get_audio_file_name(img_filename), 'wb')
    afh.write(b64decode(audio_b64))
    afh.close()

    image_b64 = xmp[u'http://ns.google.com/photos/1.0/image/'][1][1]

    ifh = open(get_second_image_name(img_filename), 'wb')
    ifh.write(b64decode(image_b64))
    ifh.close()

@main.errorhandler(404)
def page_not_found(e):
    return render_error_page(404), 404

@main.app_errorhandler(500)
def page_not_found(e):
    return render_error_page(500), 400

def render_error_page(status_code: int):
    return render_template('error_page.html', status_code=status_code)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one()
        login_user(user)

        flash('Logged in successfully.', 'success')
        return redirect(request.args.get('next') or url_for('.home'))

    return render_template('login.html', form=form)


@main.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'success')

    return redirect(url_for('.home'))


@main.route('/restricted')
@login_required
def restricted():
    return 'You can only see this if you are logged in!', 200
