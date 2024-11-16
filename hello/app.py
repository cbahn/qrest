import click
import os
from flask import Flask, g, flash, make_response, request, render_template, redirect, url_for
from pymongo import MongoClient
from crypto_module import CryptoManager, DecryptionError
from mongo_module import DatabaseManager
from config import Config
from util_module import Util
from html import escape # this is being used for bebugging
import re
import datetime
import json


app = Flask(__name__)
app.secret_key = 'my super secret key'.encode('utf8')
crypto_mgr = CryptoManager()
crypto_mgr.init(Config.COOKIE_ENCRYPTION_KEY)

# Throw an exception if the cert file is missing
if not os.path.isfile(Config.MONGO_CERT_PATH):
    raise FileNotFoundError(f"Certificate file '{Config.MONGO_CERT_PATH}' does not exist.")

# Connect to database using mongo_module.py module
mongoDB_client = MongoClient(Config.MONGO_URI, tls=True, tlsCertificateKeyFile=Config.MONGO_CERT_PATH)
db = DatabaseManager(mongoDB_client[Config.DATABASE_NAME])


START_TIME = datetime.datetime.strptime(Config.START_TIME, "%Y-%m-%d %H:%M:%S")

# a custom exception for when no cookie is found
class NoCookieError(Exception):
    pass

# a custom exception for when a user session can't be found
class SessionNotFoundError(Exception):
    pass


def read_cookie(cookie_raw):
    if cookie_raw:
        cookie = json.loads(crypto_mgr.decrypt_message(cookie_raw))
        return cookie
    else:
        raise NoCookieError()

@app.before_request
def check_session():
    # Valid Cookie is manditory unless one of these paths are used
    whitelisted_paths = ('index','new_loc', 'submit_new_user', 'login')
    user_data = None # Is there a better way of init
    try:
        cookie = read_cookie(request.cookies.get(Config.COOKIE_NAME))
        user_data = db.get_session(cookie['sessionID'])
        if user_data == None:
            raise SessionNotFoundError()

    except (NoCookieError, DecryptionError, json.JSONDecodeError, KeyError, SessionNotFoundError) as e:
        g.user_data = None
        if request.endpoint not in whitelisted_paths:
            return redirect('http://localhost:5000', code=303)
    
    g.user_data = user_data
    


@app.route('/')
def index():

    if g.user_data is None:
        return render_template('sad_panda.html')
    
    return render_template('index.html', display_text='Your cookie:{}<br>Starttime: {}'.format(str(g.user_data), START_TIME))

@app.route('/new_adventurer')
def new_adventurer():
    return render_template('new_adventurer.html')

@app.route('/wait')
def wait():
    return render_template('wait.html', start_time = '2024-11-07T13:34:40', redirect_to = url_for('index'))

@app.route('/settings')
def settings():
    return render_template('settings.html', login_code="A5BIGBROWNFOX")

# A list of all locations a user has found / solved
@app.route('/locations')
def locations():

    result = db.list_user_visits(g.user_data['userID'])
    return render_template('locations.html', locations=result)

@app.route('/TEST_qr')
def test_qr():
    return render_template('TEST_qr.html', qr_code=Util.generate_qr_code("https://qrest.xyz/n/ABX235235"))

@app.route('/submit_new_user', methods=['POST'])
def submit_new_user():

    new_username = request.form.get('new_username')
    visited_locationID = request.form.get('locationID')

    # # Usernames can only have letters, numbers, and underscores
    # # they have to be between 1 and 25 characters long
    # if re.fullmatch( r'^[a-zA-Z0-9_]{1,25}$', new_username) is None:
    #     flash("username wasn't allowed for some reason")
    #     return redirect('http://localhost:5000/welcome', code=303)
    
    # If not logged in, create a new account for them
    
    #Keep trying to generate a new ID until one is found that's not in use
    is_taken = "placeholder text"
    while is_taken is not None:
        new_userID = Util.generate_new_userID()
        is_taken = db.get_user(new_userID)
    
    sessionID = Util.generate_session_code()
    db.create_new_user(new_userID, sessionID)

    # Set the cookie
    cookie_data = { 'sessionID': sessionID }
    cookie = crypto_mgr.encrypt_message(json.dumps(cookie_data))

    # We have to define the response before setting the cookie
    response = redirect('http://localhost:5000/welcome', code=303)
    response.set_cookie(Config.COOKIE_NAME, cookie, max_age=60 * 60 * 24 * 15)  # Expires in 15 days

    # !security there's no check that users are allowed to update their name
    # We're relying entirely on them not resubmitting the POST request
    db.set_user_friendly_name(new_userID, new_username)
    db.log_visit(new_userID, visited_locationID, TEST_number="52333")
    return response

@app.route('/welcome')
def welcome():
    return render_template('welcome.html', username = g.user_data['friendly_name'])

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')

# Information about a specific location
# Cannot be accessed until the user has found the location
@app.route("/location/<loc_slug>")
def loc_info(loc_slug):
    loc_data = db.get_location_by_slug(loc_slug)

    if loc_data == None:
        return '<h1>Location not found</h1>'

    return render_template('location.html', location=loc_data)

# Logging a new location
@app.route("/n/<location_code>")
def new_loc(location_code):

    # I am having trouble finding documentation related to what type of input
    #  sanitation is needed for pymongo queries. I'll do a basic character
    #  filter here and hope it's good enough.
    remove_chars = {'{': None, '}': None, ',': None, '$': None, ';': None}
    location_code = location_code.translate(str.maketrans(remove_chars))

    # Check that location code is valid
    location_info = db.get_location_info(location_code)
    if location_info is None:
        return "Location does not exist 404: your " + location_code

    # Check if user is logged in
    if g.user_data is None:
        return render_template('new_adventurer.html',locationID=location_code)
    else:
        result = db.log_visit(g.user_data['userID'], location_code, "92")
        if result is None:
            return "You've already visited, loser"
        return "New location visited, loser"