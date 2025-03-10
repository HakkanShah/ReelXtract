from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import re
import requests
from pytube import YouTube

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/download', methods=['POST'])
def download_reel():
    try:
        data = request.get_json()
        reel_url = data.get("url")

        if not reel_url:
            return jsonify({"error": "No URL provided"}), 400

        # Extract reel ID using regex
        match = re.search(r"reel/([A-Za-z0-9_-]+)", reel_url)
        if not match:
            return jsonify({"error": "Invalid Instagram Reel URL"}), 400
        
        reel_id = match.group(1)
        
        # Convert Instagram Reel link to a downloadable format
        response = requests.get(f"https://www.instagram.com/reel/{reel_id}/?__a=1&__d=dis")
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch reel data"}), 500
        
        json_data = response.json()
        video_url = json_data["graphql"]["shortcode_media"]["video_url"]
        
        # Download the video using pytube
        yt = YouTube(video_url)
        video_stream = yt.streams.get_highest_resolution()
        video_path = os.path.join(DOWNLOAD_FOLDER, f"{reel_id}.mp4")
        video_stream.download(filename=video_path)

        # Send the file to user for direct download
        return send_file(video_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
