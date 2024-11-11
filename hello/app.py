# -*- coding: utf-8 -*-
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


app = Flask(__name__)
app.secret_key = 'my super secret key'.encode('utf8')
crypto_mgr = CryptoManager()
crypto_mgr.init(Config.COOKIE_ENCRYPTION_KEY)

# Throw an exception if the cert file is missing
if not os.path.isfile(Config.MONGO_CERT_PATH):
    raise FileNotFoundError(f"Certificate file '{Config.MONGO_CERT_PATH}' does not exist.")

mongoDB_client = MongoClient(Config.MONGO_URI, tls=True, tlsCertificateKeyFile=Config.MONGO_CERT_PATH)
db = DatabaseManager(mongoDB_client[Config.DATABASE_NAME])

START_TIME = datetime.datetime.strptime(Config.START_TIME, "%Y-%m-%d %H:%M:%S")

# function for checking that cookie decoding is successful
class NoCookieError(Exception):
    pass

def read_cookie(cookie_raw):
    if cookie_raw:
        cookie = crypto_mgr.decrypt_message(cookie_raw)
        return cookie
    else:
        raise NoCookieError()

@app.before_request
def check_session():

    # Skip validation for specific endpoints if needed
    # (endpoint referrs to the name of the view function, not the URL path)
    if request.endpoint in ('index', 'static', 'new_loc', 'wait'):
        return
    
    try:
        cookie = read_cookie(request.cookies.get(Config.COOKIE_NAME))
    except (NoCookieError, DecryptionError) as e:
        return redirect('http://localhost:5000', code=303)
    
    user_data = db.get_session(cookie)
    if user_data == None:
        return redirect('http://localhost:5000', code=303)

    # Store user data in g, a global variable tied to this one request
    g.user_data = user_data
    return


@app.route('/')
def index():
    try:
        cookie = read_cookie(request.cookies.get(Config.COOKIE_NAME))
    except NoCookieError:
        return 'SadPanda: No cookie'
    except DecryptionError:
        response = make_response('SadPanda: Cookie invalid')
        response.set_cookie(Config.COOKIE_NAME, '', expires=0) #Delete the cookie
        return response
    
    return '<h1>Hello, {}<br>Starttime: {}</h1>'.format(cookie, START_TIME)

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/wait')
def wait():
    return render_template('wait.html', start_time = '2024-11-07T13:34:40', redirect_to = 'http://localhost:5000')

@app.route('/pico')
def pico():
    return render_template('pico_trial.html')

@app.route('/welcome')
def welcome():

    # Check cookie
    try:
        cookie = read_cookie(request.cookies.get(Config.COOKIE_NAME))
    except (NoCookieError, DecryptionError) as e:
        return redirect('http://localhost:5000', code=303)
    user_data = db.get_user(cookie)
    if user_data == None:
        return redirect('http://localhost:5000', code=303)

    if user_data['friendly_name'] == None:
        return render_template('welcome_set_username.html')
    
    return render_template('welcome.html', friendly_name = user_data['friendly_name'])

@app.route('/settings')
def settings():
    return '<h1>Settings page</h1>'

@app.route('/locations')
def locations():
    return '<h1>locations page</h1>'

@app.route('/set_username', methods=['POST'])
def receive_username():

    new_username = request.form.get('new_username')

    # Usernames can only have letters, numbers, and underscores
    # they have to be between 1 and 25 characters long
    if re.fullmatch( r'^[a-zA-Z0-9_]{1,25}$', new_username) is None:
        flash("username wasn't allowed for some reason")
        return redirect('http://localhost:5000/welcome', code=303)
    
    # !security there's no check that users are allowed to update their name
    # We're relying entirely on them not resubmitting the POST request
    db.set_user_friendly_name(g.user_data['userID'], new_username)

    flash("username set: {}".format(new_username))
    return redirect('http://localhost:5000/home', code=303)

@app.route('/leaderboard')
def leaderboard():
    return '<h1>Leaderboard</h1>'

# Location information
@app.route("/location/<loc_slug>")
def loc_info(loc_slug):
    loc_data = db.get_location_by_slug(loc_slug)

    if loc_data == None:
        return '<h1>Location not found</h1>'

    return '<h1> Location name: {} </h1><br>'.format(loc_data["friendlyName"])

# Logging a new location
@app.route("/n/<location_code>")
def new_loc(location_code):

    # Check if user is logged in
    try:
        cookie = read_cookie(request.cookies.get(Config.COOKIE_NAME))
    except NoCookieError:
        cookie = ""
    except DecryptionError:
        cookie = ""

    user_data = db.get_session(cookie)
    if user_data is None:
        # If not logged in, create a new account for them
        
        #Keep trying to generate a new ID until one is found that's not in use
        is_taken = "id already in use"
        while is_taken is not None:
            new_userID = Util.generate_new_userID()
            is_taken = db.get_user(new_userID)
        
        sessionID = Util.generate_session_code()
        db.create_new_user(new_userID, sessionID)

        # Set a new cookie for them
        cookie = crypto_mgr.encrypt_message(sessionID)
        response = make_response('placeholder text')
        response.set_cookie(Config.COOKIE_NAME, cookie, max_age=60 * 60 * 24 * 10)  # Expires in 10 days


        response.set_data("congrats, you're a new user now")
        return response

        # user_data = db.create_user()
        # create a cookie for user
        pass

    # Check if user has seen this location
        # Mark this location as seen by them
        # Update location data with who saw it
        # Update user data with what they saw
    # db.user_visits_location("hi","bye")
    return "<h1>You saw a new location</h1>"
    # else
    return "<h1>You've already seen this location</h1>"
