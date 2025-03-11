from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import instaloader
import os
import glob

app = Flask(__name__)
CORS(app)

# Configure rate limiter (optional, adjust as needed)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["10 per minute"]
)

DOWNLOAD_FOLDER = "reels"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/download', methods=['POST'])
@limiter.limit("5 per minute")  # Specific limit for this endpoint
def download_reel():
    try:
        data = request.get_json()
        reel_url = data.get("url")
        if not reel_url:
            return jsonify({"error": "No URL provided"}), 400

        # Extract shortcode from the URL
        reel_shortcode = reel_url.split("/")[-2]

        # Initialize Instaloader with a custom directory and filename pattern
        loader = instaloader.Instaloader(dirname_pattern=DOWNLOAD_FOLDER, filename_pattern="{shortcode}")
        
        # Download the reel post
        post = instaloader.Post.from_shortcode(loader.context, reel_shortcode)
        loader.download_post(post, target=DOWNLOAD_FOLDER)

        # Search for the downloaded MP4 file using glob
        video_files = glob.glob(os.path.join(DOWNLOAD_FOLDER, f"{reel_shortcode}*.mp4"))
        if not video_files:
            return jsonify({"error": "No video file found"}), 500

        video_path = video_files[0]
        return send_file(video_path, as_attachment=True)

    except Exception as e:
        error_message = f"Error occurred: {str(e)}"
        # Log the error details to error.log for further troubleshooting
        with open("error.log", "a") as f:
            f.write(error_message + "\n")
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)
