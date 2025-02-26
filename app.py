import os
import json
import zipfile
import shutil
from flask import Flask, render_template, request

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

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

  
    zip_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(zip_path)

    
    extract_path = os.path.join(app.config["UPLOAD_FOLDER"], "extracted")

   
    shutil.rmtree(extract_path, ignore_errors=True)
    os.makedirs(extract_path, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        
        os.remove(zip_path)

      
        target_folder = os.path.join(extract_path, "connections", "followers_and_following")


        if not os.path.exists(target_folder):
            raise FileNotFoundError("Folder followers_and_following tidak ditemukan dalam ZIP!")

        followers_file = os.path.join(target_folder, "followers_1.json")
        following_file = os.path.join(target_folder, "following.json")

        if not os.path.exists(followers_file) or not os.path.exists(following_file):
            raise FileNotFoundError("File followers_1.json atau following.json tidak ditemukan dalam ZIP!")
        with open(followers_file, "r", encoding="utf-8") as f:
            followers_data = json.load(f)

        with open(following_file, "r", encoding="utf-8") as f:
            following_data = json.load(f)
            
        followers = [j["value"] for i in followers_data for j in i["string_list_data"]]
        following = [j["value"] for i in following_data["relationships_following"] for j in i["string_list_data"]]

        not_following_back = [user for user in following if user not in followers]

    except Exception as e:
        return {"error": str(e)}

    finally:
        shutil.rmtree(extract_path, ignore_errors=True)

    return render_template("result.html", not_following_back=not_following_back)

if __name__ == "__main__":
    app.run(debug=True)
