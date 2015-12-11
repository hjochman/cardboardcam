import os
from os import path
from urllib.parse import urljoin
from flask import Blueprint, render_template, flash, request, redirect, url_for, abort, jsonify, session
from flask import current_app
from flask.ext.login import login_user, logout_user, login_required

from werkzeug import secure_filename

from cardboardcam.extensions import cache
from cardboardcam.forms import LoginForm, ImageForm
from cardboardcam.models import User

import magic

from basehash import base62
from hexahexacontadecimal import hexahexacontadecimal_encode_int as hh_encode_int
import xxhash

import gc
from base64 import b64decode
from libxmp.utils import file_to_dict
from libxmp import XMPFiles

main = Blueprint('main', __name__)

# upload_folder = 'uploads'
#
# @main.record
# def record_auth(setup_state):
#     global upload_folder
#     upload_folder = setup_state.app.config.get('UPLOAD_FOLDER')


def upload_dir():
    return current_app.config.get('UPLOAD_FOLDER', '/tmp')


@main.route('/', methods=['GET'])
@cache.cached(timeout=1000)
def home():
    form = ImageForm()
    filename = None
    return render_template('index.html', form=form, filename=filename)


@main.route('/about', methods=['GET'])
@cache.cached(timeout=1000)
def about():
    return render_template('about.html')


@main.route('/upload', methods=['POST'])
def upload():
    # TODO: compare CSRF token from request and session
    # http://flask.pocoo.org/snippets/3/
    # current_app.logger.debug(session['csrf_token'] + ',' + request.headers.get('X-CSRFToken', 'None'))

    file = request.files['file']
    tmp_filename = secure_filename(file.filename)
    tmp_img_path = path.join(upload_dir(), tmp_filename)
    file.save(tmp_img_path)

    # don't accept huge files
    filesize = os.stat(tmp_img_path).st_size
    if filesize > current_app.config.get('MAX_CONTENT_LENGTH', 20*1024*1024):
        abort(400)  # (Bad Request), malformed data from client

    # only accept JPEGs that have EXIF data
    if magic.from_file(tmp_img_path) != b'JPEG image data, EXIF standard':
        abort(400)  # (Bad Request), malformed data from client

    hash_id = get_hash_id(tmp_img_path)
    filename = hash_id + '.jpg'
    img_path = path.join(upload_dir(), filename)
    os.rename(tmp_img_path, img_path)

    try:
        split_vr_image(img_path)
    except:
        abort(500)

    # return jsonify({'redirect': url_for('main.result', img_filename=filename)})
    return jsonify({'result_fragment': result(img_id=hash_id), 'img_id': hash_id})
    # return redirect(url_for('main.result', img_filename=filename))


def get_hash_id(filepath):
    with open(filepath, 'rb') as file:
        hash_str = base62().encode(xxhash.xxh64(file.read()).intdigest())
        # hash_str = hh_encode_int(xxhash.xxh64(file.read()).intdigest())

    return hash_str


@main.route('/<img_id>', methods=['GET'])
def result(img_id=None):
    img_filename = img_id + '.jpg'
    upload_folder = upload_dir()
    left_img = get_image_name(img_filename, 'left')
    right_img = get_image_name(img_filename, 'right')
    left_img_filepath = path.join(upload_folder, left_img)
    right_img_filepath = path.join(upload_folder, right_img)
    audio_file = path.join(upload_folder, get_audio_file_name(img_filename))
    if path.isfile(left_img_filepath) and path.isfile(right_img_filepath) and path.isfile(audio_file):
        pass
    else:
        abort(404)

    from PIL import Image
    image = Image.open(left_img_filepath)
    aspect = float(image.size[1]) / float(image.size[0])  # height / width
    thumb_height = str(int(600 * aspect))

    audio_file_url = url_for('static', filename='uploads/' + get_audio_file_name(img_filename))
    # input_file_url = url_for('static', filename='uploads/' + img_filename)
    # second_image_url = url_for('static', filename='uploads/' + get_second_image_name(img_filename))
    # template = 'result.html'
    template = 'result_fragment.html'
    return render_template(template,
                           # input_img=input_file_url,
                           # second_img=second_image_url,
                           # audio_file_url=audio_file_url,
                           audio_file=audio_file_url,
                           left_img=left_img,
                           right_img=right_img,
                           thumb_height=thumb_height)


def get_image_name(img_filename, eye : str) -> str:
    return path.splitext(img_filename)[0] + "_%s.jpg" % eye


def get_audio_file_name(img_filename):
    return path.splitext(img_filename)[0] + "_audio.mp4"


def split_vr_image(img_filename):
    XMP_NS_GPHOTOS_IMAGE = u'http://ns.google.com/photos/1.0/image/'
    XMP_NS_GPHOTOS_AUDIO = u'http://ns.google.com/photos/1.0/audio/'

    xmpfile = XMPFiles(file_path=img_filename, open_forupdate=True)
    xmp = xmpfile.get_xmp()
    right_image_b64 = xmp.get_property(XMP_NS_GPHOTOS_IMAGE, u'GImage:Data')
    audio_b64 = xmp.get_property(XMP_NS_GPHOTOS_AUDIO, u'GAudio:Data')
    xmp.delete_property(XMP_NS_GPHOTOS_IMAGE, u'GImage:Mime')
    xmp.delete_property(XMP_NS_GPHOTOS_AUDIO, u'GAudio:Mime')
    xmp.delete_property(XMP_NS_GPHOTOS_IMAGE, u'GImage:Data')
    xmp.delete_property(XMP_NS_GPHOTOS_AUDIO, u'GAudio:Data')

    # save stripped XMP header to original image
    if xmpfile.can_put_xmp(xmp):
        xmpfile.put_xmp(xmp)
    xmpfile.close_file()

    # save the right image
    right_img_filename = get_image_name(img_filename, 'right')
    with open(right_img_filename, 'wb') as fh:
        fh.write(b64decode(right_image_b64))
    del right_image_b64
    # gc.collect()

    # add stripped XMP header to the right image
    xmpfile = XMPFiles(file_path=right_img_filename, open_forupdate=True)
    if xmpfile.can_put_xmp(xmp):
        xmpfile.put_xmp(xmp)
    xmpfile.close_file()

    del xmp
    # gc.collect()

    # save the audio
    audio_filename = get_audio_file_name(img_filename)
    with open(audio_filename, 'wb') as fh:
        fh.write(b64decode(audio_b64))
    del audio_b64
    # gc.collect()

    # rename original image
    left_img_filename = get_image_name(img_filename, 'left')
    os.rename(img_filename, left_img_filename)

    return (left_img_filename, right_img_filename, audio_filename)


@main.errorhandler(404)
def status_page_not_found(e):
    return render_error_page(404), 404


@main.app_errorhandler(500)
def status_internal_server_error(e):
    return render_error_page(500), 500


def render_error_page(status_code: int):
    return render_template('error_page_fragment.html', status_code=status_code)


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
