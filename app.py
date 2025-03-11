from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import re
import os

app = Flask(__name__)
CORS(app)

# Configure rate limiter to prevent abuse
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["5 per minute"])

DOWNLOAD_FOLDER = "reels"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "ReelXtract API is running!"})

@app.route("/download", methods=["POST"])
@limiter.limit("5 per minute")
def download_reel():
    try:
        data = request.get_json()
        reel_url = data.get("url")
        if not reel_url:
            return jsonify({"error": "No URL provided"}), 400

        # Get Instagram page content
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
        }
        response = requests.get(reel_url, headers=headers)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch Instagram page"}), 500

        # Extract video URL using regex
        video_url_match = re.search(r'"video_url":"(https:\\/\\/[^"]+)"', response.text)
        if not video_url_match:
            return jsonify({"error": "Failed to extract video URL"}), 500

        video_url = video_url_match.group(1).replace("\\/", "/")  # Fix escaped slashes

        # Download video file
        video_response = requests.get(video_url, stream=True)
        video_path = os.path.join(DOWNLOAD_FOLDER, "reel.mp4")
        with open(video_path, "wb") as file:
            for chunk in video_response.iter_content(chunk_size=1024):
                file.write(chunk)

        return send_file(video_path, as_attachment=True, mimetype="video/mp4")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
