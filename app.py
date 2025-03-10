from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import instaloader
import os

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download_reel():
    try:
        data = request.get_json()
        reel_url = data.get("url")

        if not reel_url:
            return jsonify({"error": "No URL provided"}), 400

        # Extract short code from URL
        loader = instaloader.Instaloader()
        reel_shortcode = reel_url.split("/")[-2]

        # Define filename and folder
        save_path = "reels"
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # Download the reel
        post = instaloader.Post.from_shortcode(loader.context, reel_shortcode)
        video_filename = os.path.join(save_path, f"{reel_shortcode}.mp4")

        loader.download_post(post, target=save_path)

        # Find the downloaded video file
        for file in os.listdir(save_path):
            if file.endswith(".mp4") and reel_shortcode in file:
                video_filename = os.path.join(save_path, file)
                break

        if not os.path.exists(video_filename):
            return jsonify({"error": "Download failed"}), 500

        # Send the file to user
        return send_file(video_filename, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
