from flask import Blueprint, render_template, request, current_app, g, flash
from flask import redirect, url_for, session
from marino.config import Config
from functools import wraps
from marino.db import UsersDB, LocationsDB
from marino.models import User, Location
from marino.registration.controller import create_user_d
from werkzeug.utils import secure_filename
import os
from marino.admin.controller import validate_new_location_data, extract_image_from_request

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

@registration_bp.route('/admin/gallery', methods=['GET'])
def gallery(): #TODO remove this
    # List all images in the upload folder
    files = os.listdir(os.path.join(current_app.root_path, 'static', 'uploads'))
    images = [f for f in files]
    # Generate HTML to display each image
    images_html = ''.join(
        f'<img src="/static/uploads/{img}" style="width:200px; margin:10px;">'
        for img in images
    )
    return render_template('gallery.jinja2', images_html=images_html)

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