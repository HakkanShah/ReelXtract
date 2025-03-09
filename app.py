from flask import Flask, request, jsonify
import instaloader

app = Flask(__name__)
loader = instaloader.Instaloader()

@app.route('/download', methods=['POST'])
def download_reel():
    data = request.json
    reel_url = data.get("url")
    
    if not reel_url:
        return jsonify({"error": "URL is required"}), 400

    try:
        reel_shortcode = reel_url.split("/")[-2]
        loader.download_post(instaloader.Post.from_shortcode(loader.context, reel_shortcode), target="reels")
        return jsonify({"message": "Download successful!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
