from flask import Blueprint, render_template, request, current_app, g, flash
from flask import redirect, url_for, session
from marino.config import Config
from functools import wraps
from marino.db import UsersDB
from marino.models import User
from marino.registration.controller import create_user_d
from werkzeug.utils import secure_filename
import os

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
    # Check if a file is part of the request
    if 'file' not in request.files:
        return "<h1>ERROR: no file</h1>"
    file = request.files['file']
    # If no file is selected, the browser submits an empty part without filename
    if file.filename == '':
        return redirect(request.url)
    
    # Only allow specific image file extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    UPLOAD_FOLDER = os.path.join(current_app.root_path, 'static', 'uploads')
    if file and allowed_file(file.filename):
        # Secure the filename and save the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        return redirect(url_for('admin_bp_x.gallery'))
    
@registration_bp.route('/admin/gallery', methods=['GET'])
def gallery():
    # List all images in the upload folder
    files = os.listdir(os.path.join(current_app.root_path, 'static', 'uploads'))
    images = [f for f in files]
    # Generate HTML to display each image
    images_html = ''.join(
        f'<img src="/static/uploads/{img}" style="width:200px; margin:10px;">'
        for img in images
    )
    return render_template('gallery.jinja2', images_html=images_html)