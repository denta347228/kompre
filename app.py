import fitz  
import os
import base64
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

# Fungsi untuk mengonversi halaman PDF ke gambar
def convert_pdf_page_to_jpg(pdf_path: str, output_path: str, page_number=0):
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_number)
        pix = page.get_pixmap()
        pix.save(output_path)  # Simpan sebagai gambar
    except Exception as e:
        print(f"Error saat konversi PDF ke gambar: {str(e)}")

# Fungsi untuk mengenkode gambar menjadi base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Fungsi untuk membandingkan dua berkas menggunakan API
def compare_files_via_api(image1_base64, image2_base64):
    api_key = ""
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Bandingkan berkas ini, apakah 2 berkas tersebut sama? bandingkan antar berkas, bukan gambar dalam berkas "
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image1_base64}"
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image2_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 500,
        "temperature": 0
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()

# Inisialisasi Flask
app = Flask(__name__)
app.secret_key = 'secret-key'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Pastikan folder upload ada
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Route untuk halaman utama
@app.route('/')
def index():
    return render_template('index.html')

# Route untuk upload berkas
@app.route('/upload', methods=['POST'])
def upload_files():
    if 'file1' not in request.files or 'file2' not in request.files:
        flash('Dua berkas PDF harus diunggah!')
        return redirect(request.url)

    file1 = request.files['file1']
    file2 = request.files['file2']

    if file1.filename == '' or file2.filename == '':
        flash('Dua berkas harus dipilih!')
        return redirect(request.url)

    if file1 and file2:
        filename1 = secure_filename(file1.filename)
        filename2 = secure_filename(file2.filename)

        file_path1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
        file_path2 = os.path.join(app.config['UPLOAD_FOLDER'], filename2)

        # Simpan berkas
        file1.save(file_path1)
        file2.save(file_path2)

        # Konversi halaman pertama PDF ke gambar
        output_image1 = os.path.join('static', 'output_image1.jpg')
        output_image2 = os.path.join('static', 'output_image2.jpg')

        convert_pdf_page_to_jpg(file_path1, output_image1)
        convert_pdf_page_to_jpg(file_path2, output_image2)

        # Enkode gambar ke base64
        image1_base64 = encode_image(output_image1)
        image2_base64 = encode_image(output_image2)

        # Kirim ke API dan dapatkan hasil
        api_response = compare_files_via_api(image1_base64, image2_base64)
        result = api_response.get('choices', [{}])[0].get('message', {}).get('content', 'Tidak ada hasil.')

        # Tampilkan hasil
        return render_template('result.html', result=result, image1=output_image1, image2=output_image2)

    flash('Hanya file PDF yang diperbolehkan!')
    return redirect(request.url)

if __name__ == "__main__":
    app.run(debug=True)