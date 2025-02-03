from flask import Blueprint, render_template, request, current_app, g, flash
from flask import redirect, url_for, session
from marino.config import Config
from functools import wraps
from marino.db import UsersDB
from marino.models import User
from marino.registration.controller import create_user_d
from .controller import generate_leaderboard_data

def check_login():
    cookie = request.cookies.get(Config.COOKIE_NAME)
    
    ## back door cookie value for testing
    if current_app.debug and cookie == "loggedin":
        g.user = User()
        return

    user = UsersDB.lookup(User(sessionID=str(cookie)))
    if user is not None:
        g.user = user
        return
    
    # Cookie missing or invalid. Not logged in.
    session['desired_url'] = request.url # Remember the page they tried to access
    return redirect(url_for('registration_bp_x.signup'), code=302)

# Blueprint Configuration
registration_bp = Blueprint(
    'menu_bp_x',
    __name__,
    template_folder='templates',
    static_folder='static'
)
registration_bp.before_request(check_login)

@registration_bp.route('/settings', methods=['GET'])
def settings():
    return render_template('settings.jinja2',user=g.user)

@registration_bp.route('/settings/logout', methods=['POST'])
def logout():
    flash('You have been logged out.','info')
    response = redirect(url_for('registration_bp_x.login_test'),code=302)
    # Set cookie to expire immediately
    response.set_cookie(Config.COOKIE_NAME, '', expires=0)
    return response




@registration_bp.route('/leaderboard', methods=['GET'])
def leaderboard():
    return render_template(
        'leaderboard.jinja2',
        leaderboard_data=generate_leaderboard_data()
    )

@registration_bp.route('/locations', methods=['GET'])
def locations():
    return render_template('locations.jinja2')
