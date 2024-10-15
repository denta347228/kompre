import fitz  # PyMuPDF
import os

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

# Fungsi untuk mengekstrak teks dari PDF
def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        return f"Error saat mengekstrak teks dari PDF: {str(e)}"
