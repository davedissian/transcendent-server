from flask_wtf import Form
from wtforms import TextField, PasswordField, SubmitField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Email
from transcendentserver.constants import USER
from transcendentserver.models import User

class RegistrationForm(Form):
    name = TextField('name', validators=[DataRequired()])
    email = TextField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password')
    tos = BooleanField('Agree to TOS')
    submit = SubmitField('Register')

    def validate_name(form, field):
        if User.find(field.data):
            return ValidationError('A user already has that name exists.')

    def validate_email(form, field):
        if User.query.filter_by(email=field.data).first():
            return ValidationError('An account is already registered to that email.')

    def validate_tos(form, field):
        if not field.data:
            raise ValidationError('You must accept the terms of service.')

    def validate_password(form, field):
        if len(field.data) < USER.MIN_PASSWORD_LENGTH:
            raise ValidationError('Passwords must be at least %d characters long.' %
                    USER.MIN_PASSWORD_LENGTH)

class LoginForm(Form):
    name = TextField('name', validators=[DataRequired])
    password = PasswordField('password', validators=[DataRequired])
    submit = SubmitField('Register')
