from flask import Blueprint, render_template
from ..db import UsersDB


# Blueprint Configuration
registration_bp = Blueprint(
    'registration_bp_x',
    __name__,
    template_folder='templates',
    static_folder='static'
)

@registration_bp.route('/', methods=['GET'])
def home():
    return render_template(
        'index.jinja2',
        title='Flask Blueprint Demo',
        subtitle='Demonstration of Flask blueprints in action.',
        template='home-template',
    )