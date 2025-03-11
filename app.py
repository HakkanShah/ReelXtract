from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import instaloader
import os
import glob

app = Flask(__name__)
CORS(app)

# Configure rate limiter
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["10 per minute"])

DOWNLOAD_FOLDER = "reels"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/download', methods=['POST'])
@limiter.limit("5 per minute")
def download_reel():
    try:
        data = request.get_json()
        reel_url = data.get("url")
        if not reel_url:
            return jsonify({"error": "No URL provided"}), 400

        # Extract shortcode from URL
        reel_shortcode = reel_url.split("/")[-2]

        # Initialize Instaloader with a custom directory and filename pattern
        loader = instaloader.Instaloader(dirname_pattern=DOWNLOAD_FOLDER, filename_pattern="{shortcode}")
        # Set a custom User-Agent to mimic a real browser
        loader.context.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
        })

        # Download the reel
        post = instaloader.Post.from_shortcode(loader.context, reel_shortcode)
        loader.download_post(post, target=DOWNLOAD_FOLDER)

        # Find the downloaded MP4 file
        video_files = glob.glob(os.path.join(DOWNLOAD_FOLDER, f"{reel_shortcode}*.mp4"))
        if not video_files:
            return jsonify({"error": "No video file found"}), 500

        video_path = video_files[0]
        return send_file(video_path, as_attachment=True)

    except Exception as e:
        error_message = f"Error occurred: {str(e)}"
        with open("error.log", "a") as f:
            f.write(error_message + "\n")
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)
