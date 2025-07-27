import os
import logging
import base64
from flask import Flask, render_template, request, flash, redirect, url_for, send_file, session, jsonify
from werkzeug.utils import secure_filename
import tempfile
import uuid
import json
import shutil
from utils.crypto import generate_keys, encrypt_text, decrypt_text, export_keys, import_keys
from utils.steganography import embed_text_in_image, extract_text_from_image
from PIL import Image
import io
import time
import atexit
import threading

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-steganography-secret-key")

# Configure upload and temporary folders
UPLOAD_FOLDER = tempfile.gettempdir()
TEMP_FOLDER = os.path.join(UPLOAD_FOLDER, 'stegocrypt_temp')
os.makedirs(TEMP_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'json'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMP_FOLDER'] = TEMP_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Create default RSA keys for the session
default_private_key, default_public_key = generate_keys()

# Initialize temp file tracking
temp_files = {}

def cleanup_temp_files():
    """Remove temporary files older than 1 hour"""
    current_time = time.time()
    to_delete = []
    
    for file_path, timestamp in temp_files.items():
        # If file is older than 1 hour (3600 seconds)
        if current_time - timestamp > 3600:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                to_delete.append(file_path)
            except Exception as e:
                app.logger.error(f"Error deleting temp file {file_path}: {e}")
    
    # Remove deleted files from tracking dict
    for file_path in to_delete:
        del temp_files[file_path]

def cleanup_thread_worker():
    """Background thread to clean up temporary files"""
    while True:
        cleanup_temp_files()
        time.sleep(3600)  # Run every hour

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_thread_worker, daemon=True)
cleanup_thread.start()

# Register cleanup on application exit
atexit.register(cleanup_temp_files)

def allowed_file(filename):
    """Check if file has allowed extension"""
    if not filename:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'image' not in request.files:
            flash('No image selected', 'danger')
            return redirect(request.url)
        
        file = request.files['image']
        text = request.form.get('text', '')
        encryption_method = request.form.get('encryption_method', 'default')
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No image selected', 'danger')
            return redirect(request.url)
        
        if not text:
            flash('No text provided to hide', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            try:
                # Create a temporary file for the uploaded image
                temp_image_path = os.path.join(app.config['TEMP_FOLDER'], 
                                              secure_filename(file.filename))
                file.save(temp_image_path)
                
                # Track for cleanup
                temp_files[temp_image_path] = time.time()
                
                # Process the saved image
                img = Image.open(temp_image_path)
                
                # Make sure image is RGB (convert if it's not)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Create a unique ID for this encryption session
                encryption_id = uuid.uuid4().hex
                
                # Define variables for encryption output
                encrypted_text = None
                keys_data = None
                
                # Encrypt based on the selected method
                if encryption_method == 'default':
                    # Use the default keys
                    private_key, public_key = default_private_key, default_public_key
                    encrypted_text = encrypt_text(text, public_key)
                    session['using_custom_keys'] = False
                    
                elif encryption_method == 'custom':
                    # Generate new keys for this encryption
                    private_key, public_key = generate_keys()
                    
                    # Export the keys for download
                    keys_data = export_keys(private_key, public_key)
                    encrypted_text = encrypt_text(text, public_key)
                    session['using_custom_keys'] = True
                
                # Embed encrypted text in image
                stego_img = embed_text_in_image(img, encrypted_text)
                
                # Generate a filename for the stego image
                stego_filename = f"stego_image_{encryption_id}.png"
                stego_path = os.path.join(app.config['TEMP_FOLDER'], stego_filename)
                
                # Save the stego image to a temporary file
                stego_img.save(stego_path)
                
                # Track the temporary file for cleanup
                temp_files[stego_path] = time.time()
                
                # Store the filenames in session (not the actual file data)
                session['stego_image_path'] = stego_path
                session['stego_image_filename'] = stego_filename
                
                # If using custom keys, save them to a temporary file too
                if encryption_method == 'custom' and keys_data:
                    # Create a JSON file for the keys
                    keys_filename = f"stegocrypt_keys_{encryption_id}.json"
                    keys_path = os.path.join(app.config['TEMP_FOLDER'], keys_filename)
                    
                    # Write the keys to the file
                    with open(keys_path, 'w') as f:
                        json.dump(keys_data, f, indent=2)
                    
                    # Track the temporary file for cleanup
                    temp_files[keys_path] = time.time()
                    
                    # Store the path in session
                    session['keys_path'] = keys_path
                    session['keys_filename'] = keys_filename
                
                # Flag that the steganography was successful
                session['stego_successful'] = True
                
                # Return the encrypted result page
                return render_template('encrypt_result.html', 
                                      encryption_method=encryption_method)
                
            except Exception as e:
                app.logger.error(f"Error in encryption process: {str(e)}")
                flash(f'Error processing image: {str(e)}', 'danger')
                return redirect(request.url)
        else:
            flash('Allowed image types are png, jpg and jpeg', 'warning')
            return redirect(request.url)
            
    return render_template('encrypt.html')

@app.route('/get-stego-image')
def get_stego_image():
    # Get stego image path from session
    stego_path = session.get('stego_image_path')
    filename = session.get('stego_image_filename')
    
    if not stego_path or not filename or not os.path.exists(stego_path):
        flash('No steganography image available', 'danger')
        return redirect(url_for('encrypt'))
    
    # Send the file for download
    return send_file(
        stego_path,
        as_attachment=True,
        download_name=filename,
        mimetype='image/png'
    )

@app.route('/get-keys')
def get_keys():
    # Get keys path from session
    keys_path = session.get('keys_path')
    filename = session.get('keys_filename')
    
    if not keys_path or not filename or not os.path.exists(keys_path):
        flash('No encryption keys available', 'danger')
        return redirect(url_for('encrypt'))
    
    # Send the file for download
    return send_file(
        keys_path,
        as_attachment=True,
        download_name=filename,
        mimetype='application/json'
    )

@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'image' not in request.files:
            flash('No image selected', 'danger')
            return redirect(request.url)
        
        file = request.files['image']
        use_custom_keys = 'use_custom_keys' in request.form
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No image selected', 'danger')
            return redirect(request.url)
        
        # Determine decryption method based on checkbox
        decryption_method = 'custom' if use_custom_keys else 'default'
        
        # If using custom keys, check if key file is provided
        keys_file = None
        if decryption_method == 'custom':
            if 'keyfile' not in request.files:
                flash('No key file selected for custom decryption', 'danger')
                return redirect(request.url)
            
            keys_file = request.files['keyfile']
            if keys_file.filename == '':
                flash('No key file selected for custom decryption', 'danger')
                return redirect(request.url)
            
            # Check if the file is allowed
            if not allowed_file(keys_file.filename):
                flash('Invalid key file format. Must be a JSON file', 'warning')
                return redirect(request.url)
            
            # Check if the file has a .json extension
            if not keys_file.filename.lower().endswith('.json'):
                flash('Invalid key file format. Must be a JSON file', 'warning')
                return redirect(request.url)
            
        if file and allowed_file(file.filename):
            try:
                # Save the uploaded image to a temporary file
                temp_image_path = os.path.join(app.config['TEMP_FOLDER'], 
                                              secure_filename(file.filename))
                file.save(temp_image_path)
                
                # Track for cleanup
                temp_files[temp_image_path] = time.time()
                
                # Process the saved image
                img = Image.open(temp_image_path)
                
                # Extract text from image
                encrypted_text = extract_text_from_image(img)
                
                # Determine decryption method
                if decryption_method == 'default':
                    # Use default private key
                    decryption_key = default_private_key
                    
                elif decryption_method == 'custom' and keys_file:
                    # Save the uploaded key file to a temporary file
                    temp_keys_path = os.path.join(app.config['TEMP_FOLDER'], 
                                                secure_filename(keys_file.filename))
                    keys_file.save(temp_keys_path)
                    
                    # Track for cleanup
                    temp_files[temp_keys_path] = time.time()
                    
                    # Load custom keys from the saved file
                    with open(temp_keys_path, 'r') as f:
                        keys_data = json.load(f)
                    
                    decryption_key, _ = import_keys(keys_data)
                else:
                    flash('Invalid decryption method or missing keys', 'danger')
                    return redirect(request.url)
                
                # Decrypt the text
                decrypted_text = decrypt_text(encrypted_text, decryption_key)
                
                # Return the result
                return render_template('decrypt.html', decrypted_text=decrypted_text)
                
            except Exception as e:
                app.logger.error(f"Error in decryption process: {str(e)}")
                flash(f'Error extracting or decrypting text from image: {str(e)}', 'danger')
                return redirect(request.url)
        else:
            flash('Allowed image types are png, jpg and jpeg', 'warning')
            return redirect(request.url)
            
    return render_template('decrypt.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)