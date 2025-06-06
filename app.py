from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import pymssql

app = Flask(__name__)
CORS(app)

def slugify(text):
    return (
        text.lower()
        .replace("ç", "c").replace("ğ", "g")
        .replace("ı", "i").replace("ö", "o")
        .replace("ş", "s").replace("ü", "u")
        .replace(" ", "-")
    )

def get_sql_connection():
    return pymssql.connect(
        server="localhost\\SQLEXPRESS",  # Render'da çalışacaksa dış SQL'e bağlanacak adres olmalı
        user="",                         # SQL kullanıcı adı (gerekiyorsa)
        password="",                     # SQL şifresi (gerekiyorsa)
        database="BMStock"
    )

@app.route("/", methods=["POST"])
def get_image_by_barkod():
    data = request.get_json()
    barkod = data.get("barkod")

    if not barkod:
        return jsonify({"error": "Barkod eksik"})

    try:
        conn = get_sql_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT UrunAdi, Renk, Kategori
            FROM Products
            WHERE Barkod = %s
        """, (barkod,))
        row = cursor.fetchone()

        if not row:
            return jsonify({"image_url": "Bulunamadı", "error": "Ürün bulunamadı"})

        urun_adi, renk, kategori = row
        slug_url = f"https://www.bluemint.com/tr/{slugify(urun_adi)}-{slugify(renk)}-{slugify(kategori)}/"
        headers = {"User-Agent": "Mozilla/5.0"}

        res = requests.get(slug_url, headers=headers)
        html = res.text
        match = re.search(r'<meta property="og:image" content="([^"]+)"', html)

        if match:
            return jsonify({"image_url": match.group(1)})
        else:
            return jsonify({"image_url": "Bulunamadı"})

    except Exception as e:
        return jsonify({"image_url": "Hata", "error": str(e)})

@app.route("/", methods=["GET"])
def home():
    return "✅ Sunucu çalışıyor. POST ile barkod gönderin."
