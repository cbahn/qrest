from flask import Blueprint, render_template, flash, redirect, url_for, g
from flask import request, current_app, session
from marino.models import User, Location
from marino.db import UsersDB, LocationsDB
from marino.config import Config
import re
from functools import wraps

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
    'location_bp_x',
    __name__,
    template_folder='templates',
    static_folder='static'
)
registration_bp.before_request(check_login)

@registration_bp.route('/location_test', methods=['GET'])
def location_test():
    return render_template(
        'location_test.jinja2',
        title='Flask LOCATION Blueprint Demo',
        subtitle=f'subtitle fun',
        template='home-template',
    )

@registration_bp.route('/l/<loc_code>', methods=['GET'])
def new_location(loc_code):

    # Strip non-allowed characters from string
    allowed_chars = "a-zA-Z0-9"
    loc_code = re.sub(f"[^{allowed_chars}]", "", loc_code)
    
    loc = LocationsDB.lookup(Location(locationID=loc_code))
    if loc is None:
        return f"Can't find the location with ID: {loc_code}"
    
    if LocationsDB.record_visit(userID=g.user.userId, locationID=loc.locationID):
        # Set a flash that a new location has been discovered
        flash("You discovered a new location",'success')

    return redirect(url_for('location_bp_x.location', loc_slug=loc.slug))

@registration_bp.route('/location/<loc_slug>', methods=['GET'])
def location(loc_slug):
    loc = LocationsDB.lookup(Location(slug=loc_slug))
    if loc is None:
        return f"Can't find the location with slug: {loc_slug}"
    
    # Don't allow a user to view the page unless they've already visited
    print(f"userID = {g.user.userId}, locationID={loc.locationID}")
    if not LocationsDB.check_visit(userID=g.user.userId, locationID=loc.locationID):
        return f"You haven't visited this location"
    
    return render_template('location.jinja2', loc=loc)