from flask import Blueprint, render_template, request, current_app, g, flash
from flask import redirect, url_for, session
from marino.config import Config
from functools import wraps
from marino.db import UsersDB
from marino.models import User
from marino.registration.controller import create_user_d
# from .controller import generate_leaderboard_data

# Blueprint Configuration
registration_bp = Blueprint(
    'admin_bp_x',
    __name__,
    template_folder='templates',
    static_folder='static'
)

@registration_bp.route('/admin', methods=['GET'])
def admin():
    return render_template('admin.jinja2')