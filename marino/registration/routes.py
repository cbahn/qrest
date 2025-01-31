from flask import Blueprint, render_template, request, current_app, g, flash
from flask import redirect, url_for
from marino.config import Config
from functools import wraps
from marino.db import UsersDB
from marino.models import User
from marino.registration.controller import create_user_d
import re

def require_login(my_route):
    @wraps(my_route)
    def decorated_func(*args, **kwargs):
        cookie = request.cookies.get(Config.COOKIE_NAME)
        
        ## back door cookie value for testing
        if current_app.debug and cookie == "loggedin":
            g.user = User()
            return my_route(*args,**kwargs)

        user = UsersDB.lookup(User(sessionID=str(cookie)))
        if user is not None:
            g.user = user
            return my_route(*args, **kwargs)
        else:
            return render_template(
                'index.jinja2',
                title='YALL LOGGED OUT',
                subtitle='please login before you hurt yourself.',
                template='home-template',
            )
    return decorated_func

# Blueprint Configuration
registration_bp = Blueprint(
    'registration_bp_x',
    __name__,
    template_folder='templates',
    static_folder='static'
)

@registration_bp.route('/', methods=['GET'])
@require_login
def home():
    return render_template(
        'index.jinja2',
        title='Flask Blueprint Demo',
        subtitle=f'Your username is {g.user.userId}',
        template='home-template',
    )


@registration_bp.route('/login',methods=['GET'])
def login():
    return render_template('login.jinja2')


@registration_bp.route('/signup',methods=['GET'])
def signup():
    return render_template('signup.jinja2')


@registration_bp.route('/newuser',methods=['POST'])
def newuser():

    new_username = str(request.form.get('new_username'))

    # Strip non-allowed characters from string
    allowed_chars = "a-zA-Z0-9_"
    new_username = re.sub(f"[^{allowed_chars}]", "", new_username)

    duplicate_user = UsersDB.lookup(User(friendlyName=new_username))
    if duplicate_user is not None:
        flash(f"Username '{new_username}' is already taken. Please try another", "error")
        return redirect(url_for('registration_bp_x.signup'),code=302)

    result = create_user_d(new_username)

    if result is None:
        return "Username created"
    return "FAIL: " + result