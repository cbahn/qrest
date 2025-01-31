from flask import Blueprint, render_template, request, current_app, g
from marino.config import Config
from functools import wraps
from marino.db import UsersDB
from marino.models import User

def require_login(my_route):
    @wraps(my_route)
    def decorated_func(*args, **kwargs):
        cookie = request.cookies.get(Config.COOKIE_NAME)
        
        ## back door cookie value for testing
        if current_app.debug and cookie == "loggedin":
            return my_route(*args,**kwargs)

        user = UsersDB.lookup(User(sessionID=str(cookie)))
        if user is not None:
            g.user = user
            return my_route(*args, **kwargs)
        else:
            return render_template(
                'index.jinja2',
                title='YALL LOGGED OUT',
                subtitle='please login before you hurt yourself.',
                template='home-template',
            )
    return decorated_func

# Blueprint Configuration
registration_bp = Blueprint(
    'registration_bp_x',
    __name__,
    template_folder='templates',
    static_folder='static'
)

@registration_bp.route('/', methods=['GET'])
@require_login
def home():
    return render_template(
        'index.jinja2',
        title='Flask Blueprint Demo',
        subtitle=f'Your username is {g.user.userId}',
        template='home-template',
    )