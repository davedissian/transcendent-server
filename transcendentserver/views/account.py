from flask import Blueprint, redirect, url_for, request, render_template, current_app, json, abort
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from itsdangerous import URLSafeSerializer, BadSignature, SignatureExpired
from transcendentserver.models import User
from transcendentserver.forms.user import RegistrationForm, LoginForm
from transcendentserver.utils import get_current_datetime, get_validation_link, get_serializer
from transcendentserver.constants import MAIL, USER
from transcendentserver.controls import mailer


account = Blueprint('account', 'transcendentserver')


@account.route('/register', methods=('GET', 'POST'))
def register():
    if current_user.is_authenticated():
        return redirect(url_for('account.profile'))
    reg_form = RegistrationForm(next=request.args.get('next'))
    
    if reg_form.validate_on_submit():
        try:
            new_user = User.register_new_user(
                    reg_form.name.data, 
                    reg_form.email.data, 
                    reg_form.password.data)
        except IntegrityError:
            return 'In use'
        else:
            send_email_validation(new_user)
            login_user(new_user)
    return render_template('views/account/register.html', form=reg_form)

@account.route('/login', methods=('GET', 'POST'))
def login():
    login_form = LoginForm(next=request.args.get('next'))
    if login_form.validate_on_submit():
        user = User.find(login_form.name.data)
        if not user:
            # TODO: Should never get here if the form validation is running
            abort(404)
        if user.check_password(login_form.password.data):
            login_user(user)
            return redirect(url_for('account.profile'))
    return render_template('views/account/login.html', form=login_form)

@account.route('/logout', methods=('GET', 'POST'))
@login_required
def logout():
    logout_user()
    return redirect(url_for('.login'))


@account.route('/')
@login_required
def profile():
    s =  'Profile for %s' % current_user.name
    if not current_user.validated_email:
        s += ' Please verify your email address.'
    return s

@account.route('/sendvalidation')
@login_required
def send_validation():
    if current_user.is_validated():
        return redirect(url_for('.profile'))
    send_email_validation(current_user)
    return 'Success'

def send_email_validation(new_user):
    sender = MAIL.ROBOT
    targets = [new_user.email]
    subject = 'Verify your Email Address'
    body = render_template('views/account/validation/email.html', validation_url=get_validation_link(new_user.id), user=new_user)
    priority = MAIL.PRIORITY.VALIDATION
    mailer.send_async(targets, subject, body, sender, priority)

def generate_validation_url():
    u_id = str(current_user.id)
    return json.dumps(get_validation_url(u_id))

@account.route('/validate/<payload>')
def validate_email(payload):
    '''Email address validation'''
    s = get_serializer()
    try:
        user_id = s.loads(payload, max_age=USER.VALIDATION_URL_LIFETIME)
    except SignatureExpired:
        return abort(404)
    except BadSignature:
        return abort(404)
    
    user = User.query.get_or_404(user_id)
    if user.validated_email == True:
        return abort(404)
    user.validate_email()
    return render_template('views/account/validation/success.html', user=user)
