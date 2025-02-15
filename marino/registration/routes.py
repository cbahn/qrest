from flask import Blueprint, render_template, request, current_app, g, flash
from flask import redirect, url_for, session
from marino.config import Config
from functools import wraps
from marino.db import UsersDB
from marino.models import User
from marino.util import Util
from marino.registration.controller import create_user_d
import re

# Blueprint Configuration
registration_bp = Blueprint(
    'registration_bp_x',
    __name__,
    template_folder='templates',
    static_folder='static'
)

@registration_bp.route('/hello',methods=['GET'])
def signup_or_login():
    return render_template('signup_or_login.jinja2')

@registration_bp.route('/login',methods=['GET'])
def login():
    return render_template('login.jinja2')

@registration_bp.route('/log_me_in', methods=['POST'])
def new_login():
    password = str(request.form.get('password'))

    password = password.strip() # strip whitespace
        
    user = UsersDB.lookup(User(password=password))
    if user is None:
        flash("Password not recognized.", 'warning')
        return redirect(url_for('registration_bp_x.login'))
    
    # User recognized. Cycle session and set as cookie
    new_session = UsersDB.cycleSessionID(userID=user.userID)

    flash(f"Welcome back, {user.friendlyName}.", 'success')

    # Redirect them to the URL they tried to access when they got a
    #  'logged out' error message.
    response = redirect(
        session.get('desired_url',url_for('menu_bp_x.index')),
        code=302
    )
    session.pop('desired_url', None) # removed desired_url from the session
    # Set the fresh session cookie
    response.set_cookie(Config.COOKIE_NAME, new_session, max_age=60 * 60 * 24 * 15)  # Expires in 15 days
    return response

@registration_bp.route('/signup',methods=['GET'])
def signup():
    return render_template(
        'signup.jinja2',
        localStorageData = Util.generate_new_localStorageData(),
        allow_signups = Config.ALLOW_SIGNUPS, #TODO this is only for testing
    )

@registration_bp.route('/newuser',methods=['POST'])
def newuser():
    if not Config.ALLOW_SIGNUPS: #TODO this is only for testing
        flash("Signups are currently disabled.", 'error')
        return redirect(url_for('registration_bp_x.login'))

    new_username = str(request.form.get('new_username'))
    new_password = str(request.form.get('password'))
    new_fingerprint = str(request.form.get('userdata'))

    # Strip non-allowed characters from string
    allowed_chars = "a-zA-Z0-9_-"
    new_username = re.sub(f"[^{allowed_chars}]", "", new_username)
    new_password = new_password.strip()
    new_fingerprint = re.sub(f"[^{allowed_chars}]", "", new_fingerprint)


    friendlyName_in_use = UsersDB.lookup(User(friendlyName=new_username))
    if friendlyName_in_use is not None:
        flash(f"Username '{new_username}' is already taken. Please try another name.", "error")
        return redirect(url_for('registration_bp_x.signup'),code=302)

    password_in_use = UsersDB.lookup(User(password=new_password))
    if password_in_use is not None:
        flash(f"Your password is too common. Try a more complex one.", "error")
        return redirect(url_for('registration_bp_x.signup'),code=302)

    (newly_created_user, error) = create_user_d(friendlyName=new_username,password=new_password, fingerprint=new_fingerprint)

    if newly_created_user is None:
        flash(f"An error occurred and your account could not be created. "
              f"Try again or contact support. ERROR: {error}", 'error')

        return redirect(url_for('registration_bp_x.signup'),code=302)
    
    # Setup a fresh sessionID for the new user
    new_session = UsersDB.cycleSessionID(userID=newly_created_user.userID)


    flash(f"Success. Welcome to Qrest, {new_username}!", 'success')

    # Redirect them to the URL they tried to access when they got a
    #  'logged out' error message.
    response = redirect(
        session.get('desired_url',url_for('menu_bp_x.index')),
        code=302
    )
    session.pop('desired_url', None) # Remove the session key
    # Set the fresh session cookie
    response.set_cookie(Config.COOKIE_NAME, new_session, max_age=60 * 60 * 24 * 15)  # Expires in 15 days
    return response
