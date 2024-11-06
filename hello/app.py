# -*- coding: utf-8 -*-
import click
import os
from flask import Flask, make_response, request
from pymongo import MongoClient
from crypto_module import CryptoManager, DecryptionError
from mongo_module import DatabaseManager
from config import Config
from util_module import Util
from html import escape # this is being used for bebugging


app = Flask(__name__)
crypto_mgr = CryptoManager()
crypto_mgr.init(Config.COOKIE_ENCRYPTION_KEY)

# Throw an exception if the cert file is missing
if not os.path.isfile(Config.MONGO_CERT_PATH):
    raise FileNotFoundError(f"Certificate file '{Config.MONGO_CERT_PATH}' does not exist.")

mongoDB_client = MongoClient(Config.MONGO_URI, tls=True, tlsCertificateKeyFile=Config.MONGO_CERT_PATH)
db = DatabaseManager(mongoDB_client[Config.DATABASE_NAME])


# function for checking that cookie decoding is successful
class NoCookieError(Exception):
    pass
def read_cookie(cookie_raw):
    if cookie_raw:
        cookie = crypto_mgr.decrypt_message(cookie_raw)
        return cookie
    else:
        raise NoCookieError()



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
    
    return '<h1>Hello, %s</h1>' % cookie


# bind multiple URL for one view function
@app.route('/hi')
@app.route('/hello')
def say_hello():
    return '<h1>Hello, Flask!</h1>'

@app.route('/user/<userID>')
def user_lookup(userID):
    click.echo("looking for user -"+userID+"-")
    user_data = db.get_user(userID)
    if user_data is not None:
        return '<h1> Welcome back: %s</h1>' % user_data['friendly_name']
    else:
        return '<h1> Returned None </h1>'

@app.route("/loc/<locationID>")
def loc_info(locationID):
    location_leaderboard_data = db.get_location_info(locationID)

    def generate_html_table(data):
        # Start table and headers
        table_html = "<table border='1'>"
        table_html += "<tr><th>Visitor ID</th><th>Visit Order</th></tr>"

        # Add each row
        for entry in data:
            table_html += f"<tr><td>{escape(entry['visitorID'])}</td><td>{entry['visitOrder']}</td></tr>"

        # Close table
        table_html += "</table>"
        return table_html


    return '<h1> Leaderboard </h1><br>'+generate_html_table(location_leaderboard_data)

@app.route("/l/<location_code>")
def new_loc(location_code):
    # Check if user is logged in
    try:
        cookie = read_cookie(request.cookies.get(Config.COOKIE_NAME))
    except NoCookieError:
        cookie = ""
    except DecryptionError:
        cookie = ""

    user_data = db.get_user(cookie)
    if user_data is None:
        # If not logged in, create a new account for them
        
        #Keep trying to generate a new ID until one is found that's not in use
        is_taken = "id already in use"
        while is_taken is not None:
            new_userID = Util.generate_new_userID()
            is_taken = db.get_user(new_userID)

        db.create_new_user(new_userID)

        # Set a new cookie for them
        cookie = crypto_mgr.encrypt_message(new_userID)
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


@app.route("/i/<invite_code>")
def new_invite(invite_code):
    try:
        cookie = read_cookie(request.cookies.get(Config.COOKIE_NAME))
    except NoCookieError:
        cookie = "" # it's expected that user won't have a cookie yet
    except DecryptionError:
        cookie = ""

    if db.get_user(cookie) is not None:
        return "<h1>You already have a valid account, you don't need this invite code</h1>"
    
    user_data = db.get_user(invite_code)
    if user_data is not None:
        if user_data['status'] == 'fresh':
            #Code validation successful

            #Invalidate the code
            db.update_user_status(user_data['userID'], 'used')

            #Set a cookie
            cookie = crypto_mgr.encrypt_message(user_data['userID'])
            response = make_response('<h1>Welcome newcomer: %s</h1>' % user_data['friendly_name'])
            response.set_cookie(Config.COOKIE_NAME, cookie, max_age=60 * 60 * 24 * 10)  # Expires in 10 days
            return response
        else:
            return 'That Invite code has already been used'
    else:
        return '<h1>Invalid code</h1>'



# custom flask cli command
@app.cli.command()
def hello():
    """Just say hello."""
    click.echo('Hello, Human!')
