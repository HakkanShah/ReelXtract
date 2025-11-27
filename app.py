from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import instaloader
import requests
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            os.getenv('LOG_FILE', 'app.log'),
            maxBytes=1024 * 1024,  # 1MB
            backupCount=5
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configure cache
cache = Cache(app, config={
    'CACHE_TYPE': os.getenv('CACHE_TYPE', 'simple'),
    'CACHE_DEFAULT_TIMEOUT': int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
})

# Rate limiter configuration
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[os.getenv('RATELIMIT_DEFAULT', "5 per minute")]
)

DOWNLOAD_FOLDER = "reels"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@cache.memoize(timeout=300)
def get_video_url(reel_url):
    """ Extracts the video URL from Instagram using Instaloader """
    try:
        logger.info(f"Attempting to extract video URL from: {reel_url}")
        
        # Extract shortcode
        if "/reel/" in reel_url:
            shortcode = reel_url.split("/reel/")[1].split("/")[0]
        elif "/p/" in reel_url:
            shortcode = reel_url.split("/p/")[1].split("/")[0]
        else:
            logger.warning("Could not parse shortcode from URL")
            return None

        L = instaloader.Instaloader()
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        if post.is_video:
            video_url = post.video_url
            logger.info(f"Found video URL: {video_url}")
            return video_url
        else:
            logger.warning("Post is not a video")
            return None

    except Exception as e:
        logger.error(f"Error in get_video_url: {str(e)}", exc_info=True)
        return None

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "ReelXtract API is running!"})

@app.route("/download", methods=["POST"])
@limiter.limit(os.getenv('RATELIMIT_DEFAULT', "5 per minute"))
def download_reel():
    try:
        data = request.get_json()
        reel_url = data.get("url")

        if not reel_url:
            logger.warning("No URL provided in request")
            return jsonify({"error": "No URL provided"}), 400

        if not reel_url.startswith(("https://www.instagram.com/", "https://instagram.com/")):
            logger.warning(f"Invalid URL format: {reel_url}")
            return jsonify({"error": "Invalid Instagram URL format"}), 400

        logger.info(f"Processing download request for URL: {reel_url}")
        video_url = get_video_url(reel_url)

        if not video_url:
            logger.error("Failed to extract video URL")
            return jsonify({"error": "Failed to extract video URL. The reel might be private or Instagram may have blocked access."}), 500

        # Download the video with timeout and proper headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "video/mp4,video/*;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Range": "bytes=0-"
        }
        
        timeout = int(os.getenv('CHROME_TIMEOUT', 30))
        video_response = requests.get(video_url, stream=True, timeout=timeout, headers=headers)
        
        if not video_response.ok:
            logger.error(f"Failed to download video. Status code: {video_response.status_code}")
            return jsonify({"error": "Failed to download video from Instagram"}), 500

        video_path = os.path.join(DOWNLOAD_FOLDER, "reel.mp4")
        logger.info(f"Saving video to: {video_path}")

        with open(video_path, "wb") as file:
            for chunk in video_response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)

        logger.info("Video downloaded successfully")
        return send_file(video_path, as_attachment=True, mimetype="video/mp4")

    except requests.Timeout:
        logger.error("Request timed out while downloading video")
        return jsonify({"error": "Request timed out while downloading the video"}), 504
    except Exception as e:
        logger.error(f"Unexpected error in download_reel: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
 
