import os
import shutil
import tempfile
from datetime import datetime
from os import path
import base64

import magic
from PIL import Image  # from Pillow package
import xxhash
from basehash import base62
from libxmp import XMPFiles, XMPMeta, XMPError
from libxmp.consts import XMP_NS_TIFF

from flask import Blueprint, render_template, flash, request, redirect, url_for, abort, jsonify
from flask import current_app
from flask.ext.login import login_user, logout_user, login_required
from werkzeug import secure_filename

from cardboardcam.extensions import cache
from cardboardcam.forms import LoginForm, ImageForm
from cardboardcam.models import User

XMP_NS_GPHOTOS_IMAGE = u'http://ns.google.com/photos/1.0/image/'
XMP_NS_GPHOTOS_AUDIO = u'http://ns.google.com/photos/1.0/audio/'
XMP_NS_GPHOTOS_PANORAMA = u'http://ns.google.com/photos/1.0/panorama/'


def _set_properties(xmp, namespace, prefix, **kwargs):
    """
    Takes an XMPMeta instance, an XMP namespace and prefix, and a series
    of keyword arguments. The keyword name/value pairs are added as properties
    to the XMP data. Types are automatically detected (except 'long') so that
    the correct XMPMeta.set_property_* method is used.

    :param xmp: libxmp.XMPMeta
    :param namespace: str
    :param prefix: str
    :param kwargs: dict
    """
    methods = {str: xmp.set_property,
               int: xmp.set_property_int,
               float: xmp.set_property_float,
               datetime: xmp.set_property_datetime,
               bool: xmp.set_property_bool,
               }
    for name, value in kwargs.items():
        methods[type(value)](namespace, '%s:%s' % (prefix, name), value)


# monkey patch XMPMeta with our custom method
XMPMeta.set_properties = _set_properties

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


def check_jpeg(img_path, require_xmp=False):

    message = None

    # don't accept huge files
    filesize = os.stat(img_path).st_size
    if filesize > current_app.config.get('MAX_CONTENT_LENGTH', 20 * 1024 * 1024):
        message = "Image too large."

    # only accept JPEGs
    if b'image/jpeg' not in magic.from_file(img_path, mime=True):
        message = "No JPEG data found. Is this really a Cardboard Camera VR image ?"

    if require_xmp:
        try:
            xmpfile = XMPFiles(file_path=img_path)
            xmpfile.get_xmp()
        except XMPError:
            message = "JPEG does not contain valid XMP data."

    return message


@main.route('/split/upload', methods=['POST'])
def upload_for_split():
    # TODO: compare CSRF token from request and session
    # http://flask.pocoo.org/snippets/3/
    # current_app.logger.debug(session['csrf_token'] + ',' + request.headers.get('X-CSRFToken', 'None'))

    file = request.files['file']
    tmp_filename = secure_filename(file.filename)
    tmp_img_path = path.join(upload_dir(), tmp_filename)
    file.save(tmp_img_path)

    jpeg_error_message = check_jpeg(tmp_img_path)

    if jpeg_error_message is not None:
        # (400 Bad Request), malformed data from client
        return error_page(400, message=jpeg_error_message)

    # TODO: Also check for XMP data (which can exist without EXIF data, as may be
    #       the case with images made by the joiner)
    #       ONLY check for XMP data when splitting. Images to be joined don't require it.

    hash_id = get_hash_id(tmp_img_path)
    filename = hash_id + '.jpg'
    img_path = path.join(upload_dir(), filename)
    shutil.move(tmp_img_path, img_path)

    try:
        split_vr_image(img_path)
    except Exception as e:
        abort(500)

    # return jsonify({'redirect': url_for('main.result', img_filename=filename)})
    return jsonify({'result_split_fragment': result(img_id=hash_id), 'img_id': hash_id})
    # return redirect(url_for('main.result', img_filename=filename))


@main.route('/join/upload', methods=['POST'])
def upload_for_join():
    # this is a list of all the files in the form
    files = request.files

    filepaths = []
    for file in files.values():
        if not file:
            continue
        tmp_suffix = next(tempfile._get_candidate_names())
        safe_filename = secure_filename(file.filename)
        tmp_img_path = path.join(upload_dir(), '%s.%s' % (safe_filename, tmp_suffix))
        with open(tmp_img_path, 'wb') as f:
            f.write(file.read())
        filepaths.append(tmp_img_path)

    left = None
    right = None
    audio = None
    for fp in filepaths:
        mimetype = magic.from_file(fp, mime=True)
        if b'image/jpeg' in mimetype:
            # TODO: split path to test for left right in name only
            fn = fp.lower()
            if 'left' in fn or right is not None:
                left = fp
                continue
            if 'right' in fn or left is not None:
                right = fp
                continue
        # NOTE: mimetype only every seems to be video/mp4, however I've included a few
        # other likely candidates to be inclusive. if broken audio is being reported,
        # maybe remove those others
        if mimetype in [b'video/mp4',
                        b'audio/mp4a-latm',
                        b'audio/mp4']:
            audio = fp
    
    if left is None or right is None:
        error_page(404, 'Two JPEG images with "left" and "right" in '
                        'the names are requured')
    
    if get_image_dimensions(left) != get_image_dimensions(right):
        error_page(400, 'Images must be the same dimensions')

    vr_filepath = join_vr_image(left, right, audio)
    hash_id = path.basename(vr_filepath.split('.')[0])
    return jsonify({'result_fragment': result_join(img_id=hash_id), 'img_id': hash_id})


def get_hash_id(filepath):
    with open(filepath, 'rb') as file:
        hash_str = base62().encode(xxhash.xxh64(file.read()).intdigest())
        # hash_str = hh_encode_int(xxhash.xxh64(file.read()).intdigest())

    return hash_str


@main.route('/<img_id>', methods=['GET'])
def result_join(img_id=None):
    img_filename = '%s.vr.jpg' % img_id
    img_filepath = path.join(upload_dir(), img_filename)

    if not path.isfile(img_filepath):
        abort(404)

    thumb_height = calculate_thumbnail_height(img_filepath)
    template = 'result_join_fragment.html'
    return render_template(template,
                           img_path=img_filename,
                           thumb_height=thumb_height)


@main.route('/<img_id>', methods=['GET'])
def result(img_id=None):
    img_filename = '%s.jpg' % img_id
    upload_folder = upload_dir()
    left_img = get_image_name(img_filename, 'left')
    right_img = get_image_name(img_filename, 'right')
    left_img_filepath = path.join(upload_folder, left_img)
    right_img_filepath = path.join(upload_folder, right_img)
    audio_file = path.join(upload_folder, get_audio_file_name(img_filename))
    if path.isfile(left_img_filepath) and path.isfile(right_img_filepath):
        pass
    else:
        abort(404)

    thumb_height = calculate_thumbnail_height(left_img_filepath)

    audio_file_url = None
    if path.isfile(audio_file):
        audio_file_url = url_for('static', filename='uploads/' + get_audio_file_name(img_filename))

    template = 'result_fragment.html'
    return render_template(template,
                           audio_file=audio_file_url,
                           left_img=left_img,
                           right_img=right_img,
                           thumb_height=thumb_height)


def get_image_name(img_filename: str, eye: str) -> str:
    return path.splitext(img_filename)[0] + "_%s.jpg" % eye


def get_audio_file_name(img_filename):
    return path.splitext(img_filename)[0] + "_audio.mp4"


def get_image_dimensions(img_filepath):
    image = Image.open(img_filepath)
    size = image.size
    image.close()
    return size


def calculate_thumbnail_height(img_filepath: str, thumbnail_width=600) -> int:
    """
    Calculated the height for a thumbnail image to maintain the aspect ratio,
    given the desired width.

    :param img_filepath: The path to the image file
    :type img_filepath: str
    :param thumbnail_width: The target thumbnail width
    :type thumbnail_width: int
    :return: The thumbnail height, given the target width
    :rtype: int
    """
    # calculate the thumbnail aspect ratio and height
    width, height = get_image_dimensions(img_filepath)
    aspect = float(height) / float(width)
    thumb_height = str(int(thumbnail_width * aspect))
    return thumb_height


def join_vr_image(left_img_filename, right_img_filename, audio_filename=None, output_filepath=None):

    tmp_vr_filename = next(tempfile._get_candidate_names())  # tempfile.NamedTemporaryFile().name
    shutil.copy(left_img_filename, tmp_vr_filename)

    width, height = get_image_dimensions(tmp_vr_filename)

    # TODO: if left or right jpg has existing EXIF data, take it (minus the XMP part)
    #       if there is no EXIF data, add some minimal EXIF data
    #       (eg ImageWidth, ImageLength, Orientation, DateTime)

    # TODO: consider adding this namespace - it seems to be in originals but
    #       doesn't seem to matter in practise
    # xmlns:xmp = "http://ns.adobe.com/xap/1.0/" (
    # xmp:ModifyDate (iso8660 formatted date string)

    # TODO: catch XMPError ("bad schema") here
    xmpfile = XMPFiles(file_path=tmp_vr_filename, open_forupdate=True)
    xmp = xmpfile.get_xmp()
    xmp.register_namespace(XMP_NS_GPHOTOS_PANORAMA, 'GPano')
    xmp.register_namespace(XMP_NS_GPHOTOS_IMAGE, 'GImage')
    xmp.register_namespace(XMP_NS_GPHOTOS_AUDIO, 'GAudio')
    xmp.register_namespace(XMP_NS_TIFF, 'tiff')

    # NOTE: In original Cardboard Camera photos, the GPano namespace also
    #       has these additional namespaces associated with this
    #       rdf:Description block. In practise, it seems to successfully
    #       accept the photos doing it just like this, with only the
    #       GPano namespace here (I'm not sure how to get python-xmp-toolkit
    #       to add multiple namespaces to the same section anyhow ...)
    # xmlns:GImage = "http://ns.google.com/photos/1.0/image/"
    # xmlns:GAudio = "http://ns.google.com/photos/1.0/audio/"
    # xmlns:xmpNote = "http://ns.adobe.com/xmp/note/"  (XMP_NS_XMP_Note)
    xmp.set_properties(XMP_NS_GPHOTOS_PANORAMA,
                       'GPano',
                       CroppedAreaLeftPixels=0,
                       CroppedAreaTopPixels=height - 165,
                       CroppedAreaImageWidthPixels=width,
                       CroppedAreaImageHeightPixels=height,
                       FullPanoWidthPixels=width,
                       FullPanoHeightPixels=int(height * 2.6),
                       InitialViewHeadingDegrees=180)

    xmp.set_properties(XMP_NS_TIFF,
                       'tiff',
                       ImageWidth=width,
                       ImageLength=height,
                       Orientation=0,
                       Make='vectorcult.com',
                       Model='')


    left_img_b64 = None
    with open(left_img_filename, 'rb') as fh:
        left_img_data = fh.read()
    left_img_b64 = base64.b64encode(left_img_data)
    xmp.set_property(XMP_NS_GPHOTOS_IMAGE, u'GImage:Mime', 'image/jpeg')
    xmp.set_property(XMP_NS_GPHOTOS_IMAGE, u'GImage:Data', left_img_b64.decode('utf-8'))
    del left_img_b64
    # gc.collect()

    right_img_b64 = None
    with open(right_img_filename, 'rb') as fh:
        right_img_data = fh.read()
    right_img_b64 = base64.b64encode(right_img_data)
    xmp.set_property(XMP_NS_GPHOTOS_IMAGE, u'GImage:Mime', 'image/jpeg')
    xmp.set_property(XMP_NS_GPHOTOS_IMAGE, u'GImage:Data', right_img_b64.decode('utf-8'))
    del right_img_b64
    # gc.collect()

    if audio_filename is not None:
        audio_b64 = None
        with open(audio_filename, 'rb') as fh:
            audio_data = fh.read()
        audio_b64 = base64.b64encode(audio_data)
        xmp.set_property(XMP_NS_GPHOTOS_AUDIO, u'GAudio:Mime', 'audio/mp4a-latm')
        xmp.set_property(XMP_NS_GPHOTOS_AUDIO, u'GAudio:Data', audio_b64.decode('utf-8'))
        del audio_b64
        # gc.collect()

    if xmpfile.can_put_xmp(xmp):
        xmpfile.put_xmp(xmp)
    xmpfile.close_file()

    if output_filepath is None:
        vr_filepath = path.join(upload_dir(), '%s.vr.jpg' % get_hash_id(tmp_vr_filename))
    else:
        vr_filepath = output_filepath

    shutil.move(tmp_vr_filename, vr_filepath)

    return vr_filepath


def split_vr_image(img_filename):

    # TODO: catch XMPError ("bad schema") here
    xmpfile = XMPFiles(file_path=img_filename, open_forupdate=True)
    xmp = xmpfile.get_xmp()

    right_image_b64, right_img_filename = None, None
    audio_b64, audio_filename = None, None

    if xmp.does_property_exist(XMP_NS_GPHOTOS_IMAGE, u'GImage:Data'):
        right_image_b64 = xmp.get_property(XMP_NS_GPHOTOS_IMAGE, u'GImage:Data')
        xmp.delete_property(XMP_NS_GPHOTOS_IMAGE, u'GImage:Mime')
        xmp.delete_property(XMP_NS_GPHOTOS_IMAGE, u'GImage:Data')

    if xmp.does_property_exist(XMP_NS_GPHOTOS_AUDIO, u'GAudio:Data'):
        audio_b64 = xmp.get_property(XMP_NS_GPHOTOS_AUDIO, u'GAudio:Data')
        xmp.delete_property(XMP_NS_GPHOTOS_AUDIO, u'GAudio:Mime')
        xmp.delete_property(XMP_NS_GPHOTOS_AUDIO, u'GAudio:Data')

    # save stripped XMP header to original image
    if xmpfile.can_put_xmp(xmp):
        xmpfile.put_xmp(xmp)
    xmpfile.close_file()

    if right_image_b64:
        # save the right image
        right_img_filename = get_image_name(img_filename, 'right')
        with open(right_img_filename, 'wb') as fh:
            fh.write(base64.b64decode(right_image_b64))
        del right_image_b64
        # gc.collect()

        # add stripped XMP header to the right image
        xmpfile = XMPFiles(file_path=right_img_filename, open_forupdate=True)
        if xmpfile.can_put_xmp(xmp):
            xmpfile.put_xmp(xmp)
        xmpfile.close_file()

    del xmp
    # gc.collect()

    if audio_b64:
        # save the audio
        audio_filename = get_audio_file_name(img_filename)
        with open(audio_filename, 'wb') as fh:
            fh.write(base64.b64decode(audio_b64))
        del audio_b64
        # gc.collect()

    # rename original image
    left_img_filename = get_image_name(img_filename, 'left')
    shutil.move(img_filename, left_img_filename)

    return left_img_filename, right_img_filename, audio_filename


@main.errorhandler(404)
def status_page_not_found(e):
    """
    Renders the error page shown when we call abort(404).
    :type e: int
    :return:
    """
    return error_page(404, message="Not found.")


@main.app_errorhandler(500)
def status_internal_server_error(e):
    """
    Renders the error page shown when we call abort(500).
    :type e: int
    :return:
    """
    return error_page(500, message="Something went wrong.")


def error_page(status_code: int, message=''):
    """
    Renders a custom error page with the given HTTP status code in the response.
    :type status_code: int
    :type message: str
    :return:
    """
    return render_template('error_page_fragment.html', status_code=status_code, message=message), status_code


@main.context_processor
def inject_google_analytics_code():
    """
    This makes the variable 'google_analytics_tracking_id' available for every template to use.
    :rtype: dict
    """
    tracking_id = current_app.config.get('GOOGLE_ANALYTICS_TRACKING_ID', None)
    return dict(google_analytics_tracking_id=tracking_id)


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
