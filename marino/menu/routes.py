from flask import Blueprint, render_template, request, current_app, g, flash, send_file
from flask import redirect, url_for, session, jsonify
from marino.config import Config
from marino.db import UsersDB, LocationsDB
from marino.models import User
from .controller import generate_leaderboard_data, all_locations_visited_by_user
import qrcode
import io

def check_login():
    cookie = request.cookies.get(Config.COOKIE_NAME)
    
    ## back door cookie value for testing
    if current_app.debug and cookie == "loggedin":
        g.user = User()
        return

    user = UsersDB.lookup(User(sessionID=str(cookie)))
    if user is not None:
        g.user = user
        return
    
    # Cookie missing or invalid. Not logged in.
    session['desired_url'] = request.url # Remember the page they tried to access
    return redirect(url_for('registration_bp_x.signup'), code=302)

# Blueprint Configuration
registration_bp = Blueprint(
    'menu_bp_x',
    __name__,
    template_folder='templates',
    static_folder='static'
)
registration_bp.before_request(check_login)

@registration_bp.route('/', methods=['GET'])
def index():
    return render_template('index.jinja2')

@registration_bp.route('/settings', methods=['GET'])
def settings():
    return render_template('settings.jinja2',user=g.user)

@registration_bp.route('/qr/<ephemeralID>', methods=['GET'])
def create_qr(ephemeralID):
    """
    Creates a qr code for <url>/e/<ephemeralID>
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(f"{current_app.config['PREFERRED_URL_SCHEME']}://{request.host}/e/{ephemeralID}")
    qr.make(fit=True)
    
    # Create an image from the QR Code instance
    img = qr.make_image(fill_color='black', back_color='white')
    
    # Save the image to a BytesIO object
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

@registration_bp.route('/settings/logout', methods=['POST'])
def logout():
    flash('You have been logged out.','info')
    response = redirect(url_for('menu_bp_x.index'),code=302)
    # Set cookie to expire immediately
    response.set_cookie(Config.COOKIE_NAME, '', expires=0)
    return response

@registration_bp.route('/leaderboard', methods=['GET'])
def leaderboard():
    return render_template(
        'leaderboard.jinja2',
        leaderboard_data=generate_leaderboard_data()
    )

@registration_bp.route('/locations', methods=['GET'])
def locations():
    return render_template('locations.jinja2',
        locations=all_locations_visited_by_user(g.user.userID))

@registration_bp.route('/gackcoin', methods=['GET'])
def gackcoin():
    # Every pageload we cycle the ID. Not really necessary, but it's fun.
    eID = UsersDB.cycleEphemeralID(g.user.userID)
    return render_template('gackcoin.jinja2', eID=eID, user=g.user)

@registration_bp.route('/e/<ephemeralID>', methods=['GET'])
def redirect_to_user(ephemeralID):
    """
    Redirects to the user associated with the ephemeralID
    """
    user = UsersDB.lookup(User(ephemeralID=ephemeralID))
    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    print(f"g.user.admin value is {g.user.admin}")
    if g.user.admin:
        return redirect(url_for('admin_bp_x.admin_view_user', userID = user.userID), code=302)
    
    return redirect(url_for('menu_bp_x.view_user', friendlyName = user.friendlyName), code=302)

@registration_bp.route('/get_coin_count', methods=['GET'])
def get_coin_count():
    return jsonify({'coin_count': g.user.coins})

@registration_bp.route('/user/<friendly_name>', methods=['GET'])
def user(friendly_name):
    user = UsersDB.lookup(User(friendlyName=friendly_name))
    if user is None:
        flash('User not found.','error')
        return redirect(url_for('menu_bp_x.index'), code=302)
    return render_template('view_user.jinja2', me=g.user, them=user)

@registration_bp.route('/transfer_coins', methods=['POST'])
def transfer_coins():
    data = request.json
    sender_userID = g.user.userID
    recipient_friendlyName = data.get('recipient')
    amount = data.get('amount')

    if not recipient_friendlyName or not amount:
        return jsonify({'error': 'Missing recipient or amount'}), 400

    try:
        amount = int(amount)
    except ValueError:
        return jsonify({'error': 'Amount must be an integer'}), 400

    try:
        UsersDB.transfer_coin(sender_userID, recipient_friendlyName, amount)
        return jsonify({'success': True}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred'}), 500