from flask_wtf import Form as SecureForm  # this one automatically includes a csrf_token field
from wtforms import Form  # no automatic csrf_token field
from wtforms import StringField, PasswordField, IntegerField
from wtforms import validators

from werkzeug import secure_filename
from flask_wtf.file import FileField

from cardboardcam.models import User


class JoinAdvancedXmpFields(Form):
    CroppedAreaLeftPixels = IntegerField(label=u'GPano:CroppedAreaLeftPixels',
                                         default='',
                                         validators=[validators.required(),
                                                     validators.NumberRange(min=0)])
    CroppedAreaTopPixels = IntegerField(label=u'GPano:CroppedAreaTopPixels',
                                        default='',
                                        validators=[validators.required(),
                                                    validators.NumberRange(min=0)])
    CroppedAreaImageWidthPixels = IntegerField(label=u'GPano:CroppedAreaImageWidthPixels',
                                               default='',
                                               validators=[validators.required(),
                                                           validators.NumberRange(min=0)])
    CroppedAreaImageHeightPixels = IntegerField(label=u'GPano:CroppedAreaImageHeightPixels',
                                                default='',
                                                validators=[validators.required(),
                                                            validators.NumberRange(min=0)])
    FullPanoWidthPixels = IntegerField(label=u'GPano:FullPanoWidthPixels',
                                       default='',
                                       validators=[validators.required(),
                                                   validators.NumberRange(min=0)])
    FullPanoHeightPixels = IntegerField(label=u'GPano:FullPanoHeightPixels',
                                        default='',
                                        validators=[validators.required(),
                                                    validators.NumberRange(min=0)])
    InitialViewHeadingDegrees = IntegerField(label=u'GPano:InitialViewHeadingDegrees',
                                             default=180,
                                             validators=[validators.required(),
                                                         validators.NumberRange(min=0)])


class ImageForm(SecureForm):
    image = FileField(label='Select image file')


class LoginForm(SecureForm):
    username = StringField(u'Username', validators=[validators.required()])
    password = PasswordField(u'Password', validators=[validators.optional()])

    def validate(self):
        check_validate = super(LoginForm, self).validate()

        # if our validators do not pass
        if not check_validate:
            return False

        # Does our the exist
        user = User.query.filter_by(username=self.username.data).first()
        if not user:
            self.username.errors.append('Invalid username or password')
            return False

        # Do the passwords match
        if not user.check_password(self.password.data):
            self.username.errors.append('Invalid username or password')
            return False

        return True
