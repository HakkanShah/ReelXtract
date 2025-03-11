from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import instaloader
import os
import glob
import time

app = Flask(__name__)
CORS(app)

# Configure rate limiter (prevents abuse & bans)
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["2 per minute"])

DOWNLOAD_FOLDER = "reels"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "ReelXtract API is running!"})

@app.route('/download', methods=['POST'])
@limiter.limit("2 per minute")  # Avoid bans by limiting downloads
def download_reel():
    try:
        data = request.get_json()
        reel_url = data.get("url")
        if not reel_url:
            return jsonify({"error": "No URL provided"}), 400

        # Extract shortcode from the URL
        print("Reel URL received:", reel_url)
        parts = reel_url.split("/")
        if len(parts) < 5:
            return jsonify({"error": "Invalid reel URL format"}), 400
        reel_shortcode = parts[-2]
        print("Extracted shortcode:", reel_shortcode)

        # Initialize Instaloader and set session login
        loader = instaloader.Instaloader(dirname_pattern=DOWNLOAD_FOLDER, filename_pattern="{shortcode}")

        # Load Instagram session
        session_file = "session-username"  # Replace 'username' with your IG username
        if os.path.exists(session_file):
            print("Loading Instagram session...")
            loader.load_session_from_file("username", session_file)  # Replace 'username' with your IG username
        else:
            return jsonify({"error": "Instagram session file missing. Please log in using Instaloader first."}), 500

        # Set custom User-Agent
        if hasattr(loader.context, '_session'):
            loader.context._session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
            })

        # Download the reel
        post = instaloader.Post.from_shortcode(loader.context, reel_shortcode)
        print("Post fetched successfully. Downloading now...")
        loader.download_post(post, target=DOWNLOAD_FOLDER)

        # Wait for the file to be fully downloaded
        time.sleep(2)

        # Find the downloaded MP4 file
        video_files = glob.glob(os.path.join(DOWNLOAD_FOLDER, f"{reel_shortcode}*.mp4"))
        if not video_files:
            return jsonify({"error": "No video file found. Instagram may have restricted access."}), 500

        video_path = video_files[0]
        print("Video found:", video_path)
        
        return send_file(video_path, as_attachment=True, mimetype="video/mp4")

    except Exception as e:
        error_message = f"Error occurred: {str(e)}"
        with open("error.log", "a") as f:
            f.write(error_message + "\n")
        print(error_message)
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)
