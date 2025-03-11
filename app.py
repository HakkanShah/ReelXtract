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

        # Set headers to mimic a real browser request
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/537.36"
        }
        response = requests.get(reel_url, headers=headers)

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch Instagram page"}), 500

        # Extract video URL from the Instagram page source
        video_url_match = re.search(r'"video_url":"(https:\\/\\/[^"]+)"', response.text)

        if not video_url_match:
            return jsonify({"error": "Failed to extract video URL"}), 500

        video_url = video_url_match.group(1).replace("\\/", "/")  # Fix escaped slashes

        # Download the video
        video_response = requests.get(video_url, stream=True)
        video_path = os.path.join(DOWNLOAD_FOLDER, "reel.mp4")

        with open(video_path, "wb") as file:
            for chunk in video_response.iter_content(chunk_size=1024):
                file.write(chunk)

        return send_file(video_path, as_attachment=True, mimetype="video/mp4")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))  # Render assigns port dynamically
    app.run(host="0.0.0.0", port=port, debug=True)
