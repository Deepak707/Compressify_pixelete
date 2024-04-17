import os
import sys
import tempfile
import zipfile
from PIL import Image
from flask import Flask, render_template, request, send_from_directory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['COMPRESSED_FOLDER'] = tempfile.gettempdir() + '/compressed'

def compress_image(image_path, output_path, quality):
    with Image.open(image_path) as img:
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        img.save(output_path, "JPEG", optimize=True, quality=quality)

def process_images(input_folder, output_folder, quality):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    compressed_images = []

    file_types = ('.jpg', '.jpeg', '.png')

    for file_type in file_types:
        all_images = [f for f in os.listdir(input_folder) if f.endswith(file_type)]

        for image in all_images:
            input_path = os.path.join(input_folder, image)
            output_path = os.path.join(output_folder, image)

            compress_image(input_path, output_path, quality)
            compressed_images.append(output_path)

    return compressed_images

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        quality = int(request.form.get('quality'))
        if quality < 70 or quality > 80:
            return "Quality should be between 70 and 80."

        uploaded_files = request.files.getlist("file[]")
        for file in uploaded_files:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

        compressed_images = process_images(app.config['UPLOAD_FOLDER'], app.config['COMPRESSED_FOLDER'], quality)

        zip_name = 'compressed_images.zip'
        zip_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_name)
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for image in compressed_images:
                zipf.write(image, os.path.basename(image))

        return render_template('index.html', compressed_images=compressed_images)

@app.route('/download_zip')
def download_zip():
    zip_name = request.args.get('zip_name', 'compressed_images.zip')
    return send_from_directory(app.config['UPLOAD_FOLDER'], zip_name, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
