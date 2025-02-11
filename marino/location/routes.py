from flask import Blueprint, render_template, flash, redirect, url_for, g
from flask import request, current_app, session, jsonify
from marino.models import User, Location
from marino.db import UsersDB, LocationsDB
from marino.config import Config
import re

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

@registration_bp.route('/l/<loc_code>', methods=['GET'])
def new_location(loc_code):

    # Strip non-allowed characters from string
    allowed_chars = "a-zA-Z0-9"
    loc_code = re.sub(f"[^{allowed_chars}]", "", loc_code)
    
    loc = LocationsDB.lookup(Location(locationID=loc_code))
    if loc is None:
        return f"Can't find the location with ID: {loc_code}"
    
    if LocationsDB.record_visit(
        userID=g.user.userID,
        locationID=loc.locationID,
        visit_type='discovered',
        ):
        # Set a flash that a new location has been discovered
        flash("You discovered a new location",'success')

    return redirect(url_for('location_bp_x.location', loc_slug=loc.slug))

@registration_bp.route('/location/<loc_slug>', methods=['GET'])
def location(loc_slug):
    
    loc = LocationsDB.lookup(Location(slug=loc_slug))
    if loc is None:
        return render_template('undiscovered_location.jinja2')

    visit_status = LocationsDB.check_visit(userID=g.user.userID, locationID=loc.locationID)
    
    # Users can't visit an undiscovered location unless they're an admin
    if visit_status == 'undiscovered' and not g.user.admin:
        return render_template('undiscovered_location.jinja2')
    
    print(f"visit_status={visit_status}")
    return render_template('location.jinja2', loc=loc, visit_status=visit_status)

@registration_bp.route('/location/validate_guess', methods=['POST'])
def validate_guess():
    # Extract the guess from the POSTed form data
    user_guess = request.form.get('guess', '')
    slug = request.form.get('slug','')
    
    # Strip everything except alphanumeric and make lowercase
    allowed_chars = "a-zA-Z0-9"
    user_guess = re.sub(f"[^{allowed_chars}]", "", user_guess)
    user_guess.lower()

    # Also strip the slug, just for safety
    allowed_chars = "a-z0-9-"
    slug = re.sub(f"[^{allowed_chars}]", "", slug)

    #TODO should this make a database call each time?
    # Should I do this differently?
    loc = LocationsDB.lookup(Location(slug=slug))
    if loc is None:
        return jsonify(youre='fucked') #TODO make good

    # A user can't guess on a location they haven't discovered
    visit_status = LocationsDB.check_visit(
        userID=g.user.userID,
        locationID=loc.locationID)
    
    if visit_status == 'undiscovered':
        return jsonify(youhavenot='visited') # TODO make good

    # Example: Let's assume the correct answer is "london"
    print(f"userguess: {user_guess}, answer={loc.puzzleAnswer}")
    is_correct = (user_guess == loc.puzzleAnswer)
    if is_correct:
        LocationsDB.record_visit(
            userID=g.user.userID,
            locationID=loc.locationID,
            visit_type='solved'
        )
    
    # Return the JSON response with the validation result
    return jsonify(correct=is_correct)