from flask import Blueprint, render_template, request, current_app, g, flash
from flask import redirect, url_for, session
from marino.config import Config
from functools import wraps
from marino.db import UsersDB
from marino.models import User
from marino.registration.controller import create_user_d
from .controller import generate_leaderboard_data

# Blueprint Configuration
registration_bp = Blueprint(
    'menu_bp_x',
    __name__,
    template_folder='templates',
    static_folder='static'
)

@registration_bp.route('/settings', methods=['GET'])
def settings():
    return render_template('settings.jinja2')

@registration_bp.route('/leaderboard', methods=['GET'])
def leaderboard():
    return render_template(
        'leaderboard.jinja2',
        leaderboard_data=generate_leaderboard_data()
    )

@registration_bp.route('/locations', methods=['GET'])
def locations():
    return render_template('locations.jinja2')
