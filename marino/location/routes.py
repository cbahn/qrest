from flask import Blueprint, render_template, flash, redirect, url_for, g
from flask import request, current_app, session, jsonify, abort
from marino.models import User, Location, Comment
from marino.db import UsersDB, LocationsDB, CommentsDB
from marino.config import Config
import re
import time

def check_login():
    cookie = request.cookies.get(Config.COOKIE_NAME)

    user = UsersDB.lookup(User(sessionID=str(cookie)))
    if user is not None:
        g.user = user
        return
    
    # Cookie missing or invalid. Not logged in.
    session['desired_url'] = request.url # Remember the page they tried to access
    return redirect(url_for('registration_bp_x.signup_or_login'), code=302)


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
        return render_template('location_not_found.jinja2')
    
    if LocationsDB.record_visit(
        userID=g.user.userID,
        locationID=loc.locationID,
        visit_type='discovered',
        ):
        flash("You discovered a new location!",'success')

    return redirect(url_for('location_bp_x.location', loc_slug=loc.slug))

@registration_bp.route('/location/<loc_slug>', methods=['GET'])
def location(loc_slug):
    
    loc = LocationsDB.lookup(Location(slug=loc_slug))
    if loc is None:
        return render_template('location_not_found.jinja2')

    visit_status = LocationsDB.check_visit(userID=g.user.userID, locationID=loc.locationID)
    
    # Users can't visit an undiscovered location unless they're an admin
    if visit_status == 'undiscovered':
        return render_template('unvisited_location.jinja2')
    
    if visit_status == 'solved':
        comments = CommentsDB.get_comments_for_location(loc.locationID)
        return render_template('solved_location.jinja2',loc=loc, comments=comments)
    
    return render_template('discovered_location.jinja2', loc=loc)

@registration_bp.route('/location/validate_guess', methods=['POST'])
def validate_guess():
    # Extract the guess from the POSTed form data
    user_guess = request.form.get('guess', '')
    slug = request.form.get('slug','')
    
    # Strip everything except alphanumeric and make lowercase
    allowed_chars = "a-zA-Z0-9"
    user_guess = re.sub(f"[^{allowed_chars}]", "", user_guess)
    user_guess = user_guess.lower()

    # Also strip the slug, just for safety
    allowed_chars = "a-z0-9-"
    slug = re.sub(f"[^{allowed_chars}]", "", slug)

    #TODO should this make a database call each time?
    # Should I do this differently?
    loc = LocationsDB.lookup(Location(slug=slug))
    if loc is None:
        return jsonify(error='ERROR: Location not found')

    # A user can't guess on a location they haven't discovered
    visit_status = LocationsDB.check_visit(
        userID=g.user.userID,
        locationID=loc.locationID)
    
    if visit_status == 'undiscovered':
        return jsonify(error="You can't guess at a location you have not visited")

    # Sleep for 0.7 seconds
    # This is to make it slightly more awkward to guess many times in a row
    # and also slightly more awkward to design a script to guess many times
    time.sleep(0.7)


    # This is where ~~Custom~~Answers~~ get programmed in
    # If is grayson's location, then it should have a range of answers.
    c_and_c_range = [300,1200]
    guild_passwords = ['window', 'pinch','shadow','whisper','solving this quest by reading the source code? Thats how a true thief would do it.']
    if loc.slug == 'thieves-guild':
        is_correct = (user_guess in guild_passwords)
    elif loc.slug == 'cask-and-cardboard':
        try:
            num = int(user_guess)
            is_correct = (c_and_c_range[0] <= num and num <= c_and_c_range[1])
        except ValueError:
            is_correct = False
    else:
        is_correct = (user_guess == loc.puzzleAnswer)
    
    if is_correct:
        LocationsDB.record_visit(
            userID=g.user.userID,
            locationID=loc.locationID,
            visit_type='solved'
        )
        UsersDB.modify_coins(
            userID = g.user.userID,
            coin_delta = 1,
            cause=f"Earned coin for solving {loc.locationID}")
        flash(f"You solved {loc.fullName} and earned one GACKcoin!", 'success')
    # Return the JSON response with the validation result
    return jsonify(correct=is_correct, guess=user_guess)

@registration_bp.route('/submit_comment', methods=['POST'])
def submit_comment():
    user_comment = str(request.form.get('comment', ''))
    user_comment = user_comment.replace("$","")[:280]

    slug = str(request.form.get('slug',''))

    loc = LocationsDB.lookup(Location(slug=slug))
    if loc is None:
        flash("Comment didn't post: error reading slug", 'warning')
        return redirect(url_for('menu_bp_x.index'))
    
    if len(user_comment) == 0:
        flash("Comment didn't post: cannot post empty comment", 'warning')
        return redirect(url_for('location_bp_x.location',loc_slug=loc.slug))
    
    # A user can't comment on a location they haven't solved
    visit_status = LocationsDB.check_visit(
        userID=g.user.userID,
        locationID=loc.locationID)
    
    if not visit_status == 'solved':
        flash("You cannot comment on a location you haven't solved.")
        return redirect(url_for('location_bp_x.location',loc_slug=loc.slug))
    
    CommentsDB.create_comment(g.user.userID, loc.locationID, user_comment)
    return redirect(url_for('location_bp_x.location',loc_slug=loc.slug))