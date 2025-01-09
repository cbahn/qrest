from flask import Blueprint, render_template
from ..db import create_test


# Blueprint Configuration
homerun_bp = Blueprint(
    'homerun_bp_name',
    __name__,
    template_folder='templates',
    static_folder='static'
)

@homerun_bp.route('/', methods=['GET'])
def home():

    create_test("joborn")

    """Homepage."""
    return render_template(
        'index.jinja2',
        title='Flask Blueprint Demo',
        subtitle='Demonstration of Flask blueprints in action.',
        template='home-template',
    )