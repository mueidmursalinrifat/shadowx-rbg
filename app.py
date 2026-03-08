from flask import Flask, render_template, request, jsonify, send_file
import requests
import os
from werkzeug.utils import secure_filename
import uuid
from io import BytesIO
import base64

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/remove-background', methods=['POST'])
def remove_background():
    try:
        # Check if image is uploaded or URL is provided
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                # Read the file and convert to base64 for API
                image_data = file.read()
                files = {
                    'image_file': ('image.png', image_data, 'image/png')
                }
            else:
                return jsonify({'error': 'Invalid file type'}), 400
        elif 'image_url' in request.form and request.form['image_url']:
            image_url = request.form['image_url']
            files = {
                'image_url': (None, image_url)
            }
        else:
            return jsonify({'error': 'No image provided'}), 400

        # Call remove.bg API
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files=files,
            data={'size': 'auto'},
            headers={'X-Api-Key': 'JySt55NJN52f9JMbDTLsb77e'},
            stream=True
        )

        if response.status_code == 200:
            # Convert response to base64 for sending to frontend
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            return jsonify({
                'success': True,
                'image': f'data:image/png;base64,{image_base64}'
            })
        else:
            return jsonify({'error': 'Failed to remove background'}), response.status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)