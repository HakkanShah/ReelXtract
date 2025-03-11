from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import undetected_chromedriver as uc
import requests
import os
import re
import time

app = Flask(__name__)
CORS(app)

# Rate limiter to prevent excessive requests
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["5 per minute"])

DOWNLOAD_FOLDER = "reels"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def get_video_url(reel_url):
    """ Extracts the video URL from Instagram using Undetected Selenium """
    try:
        options = uc.ChromeOptions()
        options.add_argument("--headless=new")  # Run in headless mode (no UI)
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")

        driver = uc.Chrome(options=options)
        driver.get(reel_url)
        time.sleep(5)  # Wait for the page to fully load

        page_source = driver.page_source
        driver.quit()

        # Extract the video URL from the page source
        video_url_match = re.search(r'"video_url":"(https:\\/\\/[^"]+)"', page_source)
        if video_url_match:
            return video_url_match.group(1).replace("\\/", "/")  # Fix escaped slashes

        return None
    except Exception as e:
        return None

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

        video_url = get_video_url(reel_url)

        if not video_url:
            return jsonify({"error": "Failed to extract video URL. Instagram may have blocked access."}), 500

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
