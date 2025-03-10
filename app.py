from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import instaloader
import os

app = Flask(__name__)
CORS(app)

# Ensure "reels" directory exists
if not os.path.exists("reels"):
    os.makedirs("reels")

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
        loader = instaloader.Instaloader(dirname_pattern="reels")

        # Download Reel
        post = instaloader.Post.from_shortcode(loader.context, reel_shortcode)
        loader.download_post(post, target="reels")

        # Find the downloaded file
        for file in os.listdir("reels"):
            if file.startswith(reel_shortcode) and file.endswith(".mp4"):
                file_path = os.path.join("reels", file)
                return send_file(file_path, as_attachment=True)

        return jsonify({"error": "Download failed"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
