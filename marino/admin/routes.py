from flask import Blueprint, render_template, request, current_app, g, flash
from flask import redirect, url_for, session, jsonify
from marino.config import Config
from marino.db import UsersDB, LocationsDB
from marino.models import User, Location
from werkzeug.utils import secure_filename
import os
from marino.admin.controller import validate_new_location_data, extract_image_from_request

from flask import Flask, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import qrcode
import io
import math
from PIL import Image  # Add this import


def check_login_require_admin():
    cookie = request.cookies.get(Config.COOKIE_NAME)

    user = UsersDB.lookup(User(sessionID=str(cookie)))
    if user is None:
        # Cookie missing or invalid. Not logged in.
        session['desired_url'] = request.url # Remember the page they tried to access
        return redirect(url_for('registration_bp_x.signup'), code=302)

    g.user = user
    if not user.admin:
        # TODO make a better error page
        return render_template('unauthorized.jinja2'), 403
    return

# Blueprint Configuration
registration_bp = Blueprint(
    'admin_bp_x',
    __name__,
    template_folder='templates',
    static_folder='static'
)
registration_bp.before_request(check_login_require_admin)

@registration_bp.route('/admin', methods=['GET'])
def admin():
    return render_template('admin.jinja2')

@registration_bp.route('/admin/newlocation', methods=['GET'])
def newlocation():
    return render_template('newlocation.jinja2')

@registration_bp.route('/admin/newlocation', methods=['POST'])
def upload_newlocation():

    new_loc, err = validate_new_location_data(
        fullName=request.form.get('fullName',"",type=str),
        slug=request.form.get('slug',"",type=str),
        description=request.form.get('description',"",type=str),
        puzzleText=request.form.get('puzzleText',"",type=str),
        puzzleAnswer=request.form.get('puzzleAnswer',"",type=str),
    )
    if new_loc is None:
        return f"DATA ERROR: {err}"

    file = extract_image_from_request(
        request, allowed_extensions={'.jpg', '.jpeg', '.png'})
    
    if file is None:
        return "FILE ERROR"

    UPLOAD_FOLDER = os.path.join(
        current_app.root_path, 'static', 'uploads')
    # Secure the filename and save the file
    _, ext = os.path.splitext(file.filename)
    filename = secure_filename(new_loc.slug + ext)
    new_loc.imageFile = filename
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    LocationsDB.create(new_loc)

    return redirect(url_for('location_bp_x.location',loc_slug=new_loc.slug))

@registration_bp.route('/admin/locations', methods=['GET'])
def admin_locations():
    all_locs = LocationsDB.get_all_locations()
    return render_template('admin_locations.jinja2',locations=all_locs)


@registration_bp.route('/location/<loc_slug>', methods=['DELETE'])
def delete_location(loc_slug):

    UPLOADS_FOLDER = os.path.join(current_app.root_path, 'static', 'uploads')

    loc = LocationsDB.lookup(Location(slug=loc_slug))

    # attempt to delete record from database
    result = LocationsDB.delete(loc.locationID)
    if not result:
        flash(f"Failed to delete location record {loc.locationID}", "error")
        return redirect(url_for('admin_bp_x.admin_locations'))
    flash(f"Location record {loc.locationID} deleted.", "success")

    # attempt to delete image file next
    filename_tbd = secure_filename(loc.imageFile)
    filepath_tbd = os.path.join(UPLOADS_FOLDER, filename_tbd)
    
    if not os.path.isfile(filepath_tbd):
        flash("weirdly, the imagefile for that location was already gone", "warning")
    else:
        try:
            # Attempt to delete the file
            os.remove(filepath_tbd)
        except Exception as e:
            # Return an error response if something goes wrong
            return f"Error deleting file: {str(e)}", 500
    
    return redirect(url_for('admin_bp_x.admin_locations'))

@registration_bp.route('/admin/user/<userID>', methods=['GET'])
def admin_view_user(userID):
    """
    Transfer a coin to another user
    """
    user = UsersDB.lookup(User(userID=userID))
    if user is None:
        return jsonify({"error": "User not found"}), 404

    return render_template('admin_view_user.jinja2', user=user)

@registration_bp.route('/admin/deduct_coins', methods=['POST'])
def deduct_coins():
    """
    Deduct coins from a user
    """
    data = request.get_json()
    userID = data.get('userID')
    amount_to_remove = int(data.get('coin_amount'))
    if amount_to_remove <= 0:
        return jsonify({"error": "coin_amount must be positive"}), 400

    user = UsersDB.lookup(User(userID=userID))
    if user is None:
        return jsonify({"error": "User not found"}), 404

    try:
        new_coin_count = UsersDB.modify_coins(userID, -amount_to_remove,
            f"Deducted by admin: {g.user.friendlyName}")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({'success':True,"new_coin_count": new_coin_count}), 200

@registration_bp.route("/admin/change_discovery_status", methods=["POST"])
def change_discovery_status():
    data = request.get_json()
    locationID = data.get("locationID")
    new_status = data.get("status")

    LocationsDB.change_discovery_status(g.user.userID, locationID, new_status)

    return jsonify({"success": True, "new_status": new_status})

def list_locations():
    """Dummy function returning locations with titles and QR data"""
    return [
        {"title": "Location 1", "data": "https://example.com/location1"},
        {"title": "Location 2", "data": "https://example.com/location2"},
        {"title": "Location 3", "data": "https://example.com/location3"},
    ]

@registration_bp.route("/pdf", methods=["GET"])
def generate_pdf():
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter  # dimensions in points

    locations = LocationsDB.get_all_locations()

    for location in locations:
        title = location.fullName
        qr_data = f"{current_app.config['PREFERRED_URL_SCHEME']}://{request.host}/l/{location.locationID}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=0,
            )
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)

        # Load the image from the BytesIO buffer
        qr_image = Image.open(qr_buffer)

        # Draw the title centered at the top of the page
        pdf.setFont("Helvetica-Bold", 40)
        text_width = pdf.stringWidth(title, "Helvetica-Bold", 40)
        pdf.drawString((width - text_width) / 2, height - 100, title)

        # Define the QR code's size and choose a center position for it.
        # In this case, we'll center the QR code on the page.
        qr_size = 250
        center_x = width / 2
        center_y = height / 2

        # Save the canvas state, translate to the center, rotate, draw the QR, then restore state.
        pdf.saveState()
        pdf.translate(center_x, center_y)
        pdf.rotate(135)  # rotate by 45 degrees
        pdf.drawInlineImage(qr_image, -qr_size / 2, -qr_size / 2, qr_size, qr_size)
        pdf.restoreState()

        # Draw a black circle outline around the rotated QR code.
        # For a square of side `qr_size` rotated by 45°, the bounding circle has a radius of:
        #     (qr_size * sqrt(2)) / 2
        # Adding a little padding (e.g., 10 points) gives:
        radius = (qr_size * math.sqrt(2)) / 2 + 10
        pdf.setStrokeColor(canvas.Color(0, 0, 0))
        pdf.setLineWidth(2)
        pdf.circle(center_x, center_y, radius)

        # Start a new page for the next location.
        pdf.showPage()

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True,
        mimetype='application/pdf', download_name='locations.pdf')