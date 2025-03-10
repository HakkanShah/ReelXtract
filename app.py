from flask import Flask, request, jsonify
from flask_cors import CORS
import instaloader
import traceback  # To capture errors

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

@app.route('/download', methods=['POST'])
def download_reel():
    try:
        data = request.get_json()
        reel_url = data.get("url")

        if not reel_url:
            return jsonify({"error": "No URL provided"}), 400

        # Debugging logs
        print(f"Received URL: {reel_url}")

        # Extract shortcode from URL
        loader = instaloader.Instaloader()
        reel_shortcode = reel_url.split("/")[-2]
        print(f"Extracted Shortcode: {reel_shortcode}")

        # Download the reel
        post = instaloader.Post.from_shortcode(loader.context, reel_shortcode)
        loader.download_post(post, target="reels")

        return jsonify({"message": "Download successful!", "shortcode": reel_shortcode})

    except Exception as e:
        error_message = f"Error: {str(e)}"
        print("ERROR LOG:", error_message)
        print(traceback.format_exc())  # Print full error traceback
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)
