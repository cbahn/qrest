from flask import Blueprint, render_template, request, current_app, g, flash
from flask import redirect, url_for, session
from marino.config import Config
from functools import wraps
from marino.db import UsersDB
from marino.models import User
from marino.util import Util
from marino.registration.controller import create_user_d
import re

def require_login(my_route):
    @wraps(my_route)
    def decorated_func(*args, **kwargs):
        cookie = str(request.cookies.get(Config.COOKIE_NAME))

        # Strip non-allowed characters from string
        allowed_chars = "A-Z0-9"
        cookie = re.sub(f"[^{allowed_chars}]", "", cookie)
        
        ## back door cookie value for testing
        if current_app.debug and cookie == "loggedin":
            g.user = User()
            return my_route(*args,**kwargs)

        user = UsersDB.lookup(User(sessionID=cookie))
        if user is not None:
            g.user = user
            return my_route(*args, **kwargs)
        
        # Cookie missing or invalid. Not logged in.
        session['desired_url'] = request.url # Remember the page they tried to access
        return redirect(url_for('registration_bp_x.signup'),code=302)
    return decorated_func

# Blueprint Configuration
registration_bp = Blueprint(
    'registration_bp_x',
    __name__,
    template_folder='templates',
    static_folder='static'
)

@registration_bp.route('/test', methods=['GET'])
@require_login
def login_test():
    return render_template(
        'login_test.jinja2',
        title='Flask Blueprint Demo',
        subtitle=f'Your userID is {g.user.userId}',
        template='home-template',
    )


@registration_bp.route('/login',methods=['GET'])
def login():
    return render_template('login.jinja2')

@registration_bp.route('/newlogin', methods=['POST'])
def new_login():
    userID = str(request.form.get('userID'))

    userID = userID.upper()#Capitalize so that the input is case insensitive
    allowed_chars = "A-Z0-9"
    userID = re.sub(f"[^{allowed_chars}]", "", userID)
        
    user = UsersDB.lookup(User(userId=userID))
    if user is None:
        flash("Login code not recognized. Try again.", 'warning')
        return redirect(url_for('registration_bp_x.login'))
    
    # User recognized. Cycle session and set as cookie
    new_session = UsersDB.cycleSessionID(userId=user.userId)

    flash(f"Welcome back, {user.friendlyName}.", 'success')

    # Redirect them to the URL they tried to access when they got a
    #  'logged out' error message.
    response = redirect(
        session.get('desired_url',url_for('registration_bp_x.login_test')),
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
        localStorageData = Util.generate_new_localStorageData()
    )

@registration_bp.route('/newuser',methods=['POST'])
def newuser():

    new_username = str(request.form.get('new_username'))
    new_fingerprint = str(request.form.get('userdata'))

    # Strip non-allowed characters from string
    allowed_chars = "a-zA-Z0-9_-"
    new_username = re.sub(f"[^{allowed_chars}]", "", new_username)
    new_fingerprint = re.sub(f"[^{allowed_chars}]", "", new_fingerprint)


    duplicate_user = UsersDB.lookup(User(friendlyName=new_username))
    if duplicate_user is not None:
        flash(f"Username '{new_username}' is already taken. Please try another name.", "error")
        return redirect(url_for('registration_bp_x.signup'),code=302)

    (newly_created_user, error) = create_user_d(new_username,fingerprint=new_fingerprint)

    if newly_created_user is None:
        flash(f"An error occurred and your account could not be created. "
              f"Try again or contact support. ERROR: {error}", 'error')

        return redirect(url_for('registration_bp_x.signup'),code=302)
    
    # Setup a fresh sessionID for the new user
    new_session = UsersDB.cycleSessionID(userId=newly_created_user.userId)


    flash(f"Success. Welcome to Qrest, {new_username}!", 'success')

    # Redirect them to the URL they tried to access when they got a
    #  'logged out' error message.
    response = redirect(
        session.get('desired_url',url_for('registration_bp_x.login_test')),
        code=302
    )
    session.pop('desired_url', None) # Remove the session key
    # Set the fresh session cookie
    response.set_cookie(Config.COOKIE_NAME, new_session, max_age=60 * 60 * 24 * 15)  # Expires in 15 days
    return response