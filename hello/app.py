# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2019 Grey Li
    :license: MIT, see LICENSE for more details.
"""
import click
from flask import Flask, make_response, request
from crypto_module import CryptoManager, DecryptionError

app = Flask(__name__)
cm = CryptoManager()
cm.init("Io4blYZxtHCXW2X2OMUTaPgQH7kYxR+ibRGZm3O2LRk=")

valid_codes = {"FG42CPCM":"valid", "B8H47AY4":"valid"}


# the minimal Flask application
@app.route('/')
def index():
    return '<h1>Hello, World!</h1>'

@app.route("/set_cookie")
def set_cookie():
    user_id = cm.encrypt_message("bob the crusher")  # Example user ID
    response = make_response("User cookie has been set")
    response.set_cookie("user_id", user_id, max_age=60 * 60 * 24)  # Expires in 1 day
    return response

# Route to check the user cookie
@app.route("/check_cookie")
def check_cookie():
    user_id = request.cookies.get("user_id")
    if user_id:
        decrypted = cm.decrypt_message(user_id)
        return f"User ID from cookie: {decrypted}"
    else:
        return "No user cookie found"

# bind multiple URL for one view function
@app.route('/hi')
@app.route('/hello')
def say_hello():
    return '<h1>Hello, Flask!</h1>'


@app.route('/i/<invite_code>')
def new_code(invite_code):
    invite_code = invite_code.upper()
    if not invite_code in valid_codes:
        return '<h1> Your code, %s, not recognized</h1>' % invite_code
    if valid_codes[invite_code] == 'valid':
        valid_codes[invite_code] = 'invalid'
        return '<h1> Your code, %s, was valid but is now used up</h1>' % invite_code
    elif valid_codes[invite_code] == 'invalid':
        return '<h1> Your code, %s, has been used</h1>' % invite_code




# custom flask cli command
@app.cli.command()
def hello():
    """Just say hello."""
    click.echo('Hello, Human!')
