from flask import Flask, request, jsonify
from flask_cors import CORS
import instaloader

app = Flask(__name__)
CORS(app)  # ✅ Enables CORS to allow frontend API requests

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

        # Download the reel
        loader.download_post(instaloader.Post.from_shortcode(loader.context, reel_shortcode), target="reels")

        return jsonify({"message": "Download successful!", "shortcode": reel_shortcode})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
