from flask import Flask, request, jsonify, send_from_directory
import requests
import re
from flask_cors import CORS

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

@app.route("/", methods=["POST"])
def get_image():
    data = request.get_json()
    urun_adi = data.get("urun_adi")
    renk = data.get("renk")
    kategori = data.get("kategori")

    slug_url = f"https://www.bluemint.com/tr/{slugify(urun_adi)}-{slugify(renk)}-{slugify(kategori)}/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
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
    return "✅ Sunucu çalışıyor. POST isteği gönderin."

@app.route("/ui")
def serve_ui():
    return send_from_directory("static", "index.html")