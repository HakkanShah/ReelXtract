from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import instaloader
import os
import glob

app = Flask(__name__)
CORS(app)

# Ensure "reels" directory exists
DOWNLOAD_FOLDER = "reels"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/download', methods=['POST'])
def download_reel():
    try:
        data = request.get_json()
        reel_url = data.get("url")

        if not reel_url:
            return jsonify({"error": "No URL provided"}), 400

        # Extract short code from URL
        reel_shortcode = reel_url.split("/")[-2]

        # Initialize Instaloader
        loader = instaloader.Instaloader(dirname_pattern=DOWNLOAD_FOLDER, filename_pattern="{shortcode}")

        # Download Reel
        post = instaloader.Post.from_shortcode(loader.context, reel_shortcode)
        loader.download_post(post, target=DOWNLOAD_FOLDER)

        # Find the actual downloaded MP4 file
        video_files = glob.glob(os.path.join(DOWNLOAD_FOLDER, f"{reel_shortcode}*.mp4"))
        
        if not video_files:
            return jsonify({"error": "No video file found"}), 500

        video_path = video_files[0]  # Get the first matching video file

        # Send the file to the user
        return send_file(video_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
