import os
import json
import zipfile
import shutil
from flask import Flask, render_template, request

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Pastikan folder uploads ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return {"error": "Tidak ada file yang diunggah!"}

    file = request.files["file"]
    if file.filename == "":
        return {"error": "Nama file tidak valid!"}

    if not file.filename.endswith(".zip"):
        return {"error": "Hanya menerima file ZIP!"}

    # Simpan file ZIP
    zip_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(zip_path)

    # Lokasi folder ekstraksi
    extract_path = os.path.join(app.config["UPLOAD_FOLDER"], "extracted")

    # Hapus folder ekstraksi sebelum mengekstrak file baru
    shutil.rmtree(extract_path, ignore_errors=True)
    os.makedirs(extract_path, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        # Hapus file ZIP setelah diekstrak
        os.remove(zip_path)

        # Tentukan lokasi folder followers_and_following di dalam ZIP
        target_folder = os.path.join(extract_path, "connections", "followers_and_following")

        # Pastikan folder tersebut ada
        if not os.path.exists(target_folder):
            raise FileNotFoundError("Folder followers_and_following tidak ditemukan dalam ZIP!")

        # Path file JSON yang diperlukan
        followers_file = os.path.join(target_folder, "followers_1.json")
        following_file = os.path.join(target_folder, "following.json")

        # Periksa apakah kedua file ada
        if not os.path.exists(followers_file) or not os.path.exists(following_file):
            raise FileNotFoundError("File followers_1.json atau following.json tidak ditemukan dalam ZIP!")

        # Buka dan baca file JSON
        with open(followers_file, "r", encoding="utf-8") as f:
            followers_data = json.load(f)

        with open(following_file, "r", encoding="utf-8") as f:
            following_data = json.load(f)

        # Ambil daftar followers
        followers = [j["value"] for i in followers_data for j in i["string_list_data"]]

        # Ambil daftar following
        following = [j["value"] for i in following_data["relationships_following"] for j in i["string_list_data"]]

        # Cari yang tidak follow balik
        not_following_back = [user for user in following if user not in followers]

    except Exception as e:
        return {"error": str(e)}

    finally:
        # Hapus folder ekstraksi setelah selesai membaca file JSON
        shutil.rmtree(extract_path, ignore_errors=True)

    return render_template("result.html", not_following_back=not_following_back)

if __name__ == "__main__":
    app.run(debug=True)
