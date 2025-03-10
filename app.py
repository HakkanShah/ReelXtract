from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists

@app.route('/download', methods=['POST'])
def download_reel():
    try:
        data = request.get_json()
        reel_url = data.get("url")

        if not reel_url:
            return jsonify({"error": "No URL provided"}), 400

        # Download Reel using yt_dlp
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'format': 'mp4/best',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(reel_url, download=True)
            video_filename = ydl.prepare_filename(info)

        # Send the file directly for user download
        return send_file(video_filename, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
