# -*- coding: utf-8 -*-
import click
from flask import Flask, make_response, request
from crypto_module import CryptoManager, DecryptionError
from mongo_module import DatabaseManager

app = Flask(__name__)
cm = CryptoManager()
cm.init("Io4blYZxtHCXW2X2OMUTaPgQH7kYxR+ibRGZm3O2LRk=") # Placeholder key while testing

db = DatabaseManager()

valid_codes = {"FG42CPCM":"valid", "B8H47AY4":"valid"}
COOKIE_NAME = 'qd'


# function for checking that cookie decoding is successful
class NoCookieError(Exception):
    pass
def read_cookie(cookie_raw):
    if cookie_raw:
        cookie = cm.decrypt_message(cookie_raw)
        return cookie
    else:
        raise NoCookieError()



@app.route('/')
def index():
    try:
        cookie = read_cookie(request.cookies.get(COOKIE_NAME))
    except NoCookieError:
        return 'SadPanda: No cookie'
    except DecryptionError:
        response = make_response('SadPanda: Cookie invalid')
        response.set_cookie(COOKIE_NAME, '', expires=0) #Delete the cookie
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



@app.route("/i/<invite_code>")
def new_invite(invite_code):
    try:
        cookie = read_cookie(request.cookies.get(COOKIE_NAME))
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
            cookie = cm.encrypt_message(user_data['userID'])
            response = make_response('<h1>Welcome newcomer: %s</h1>' % user_data['friendly_name'])
            response.set_cookie(COOKIE_NAME, cookie, max_age=60 * 60 * 24 * 10)  # Expires in 10 days
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
