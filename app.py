from flask import Flask, request, jsonify
import os
import instaloader

app = Flask(__name__)

@app.route("/")
def home():
    return "Instagram Reels Downloader API is running!"

@app.route("/download", methods=["POST"])
def download_reel():
    try:
        data = request.get_json()
        reel_url = data.get("url")
        if not reel_url:
            return jsonify({"error": "URL is required"}), 400
        
        loader = instaloader.Instaloader()
        loader.download_post(instaloader.Post.from_shortcode(loader.context, reel_url.split("/")[-2]), target="downloads")

        return jsonify({"message": "Download successful!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
