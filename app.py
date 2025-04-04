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
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

        driver = uc.Chrome(options=options)
        driver.get(reel_url)
        time.sleep(8)  # Increased wait time for better loading

        # Try multiple patterns to find video URL
        patterns = [
            r'"video_url":"(https:\\/\\/[^"]+)"',
            r'"video_versions":\[{"type":\d+,"url":"(https:\\/\\/[^"]+)"',
            r'<video[^>]*src="([^"]+)"',
            r'"playable_url":"(https:\\/\\/[^"]+)"'
        ]

        page_source = driver.page_source
        driver.quit()

        for pattern in patterns:
            video_url_match = re.search(pattern, page_source)
            if video_url_match:
                url = video_url_match.group(1).replace("\\/", "/")
                if url.startswith("https://"):
                    return url

        return None
    except Exception as e:
        print(f"Error in get_video_url: {str(e)}")
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

        if not reel_url.startswith(("https://www.instagram.com/", "https://instagram.com/")):
            return jsonify({"error": "Invalid Instagram URL format"}), 400

        video_url = get_video_url(reel_url)

        if not video_url:
            return jsonify({"error": "Failed to extract video URL. The reel might be private or Instagram may have blocked access."}), 500

        # Download the video with timeout
        video_response = requests.get(video_url, stream=True, timeout=30)
        if not video_response.ok:
            return jsonify({"error": "Failed to download video from Instagram"}), 500

        video_path = os.path.join(DOWNLOAD_FOLDER, "reel.mp4")

        with open(video_path, "wb") as file:
            for chunk in video_response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)

        return send_file(video_path, as_attachment=True, mimetype="video/mp4")

    except requests.Timeout:
        return jsonify({"error": "Request timed out while downloading the video"}), 504
    except Exception as e:
        print(f"Error in download_reel: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))  # Render assigns port dynamically
    app.run(host="0.0.0.0", port=port, debug=True)
