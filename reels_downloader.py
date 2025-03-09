import instaloader

# Create an instaloader instance
loader = instaloader.Instaloader()

# Instagram Reel URL (Replace with the actual Reel URL)
reel_url = "https://www.instagram.com/reel/DG1Dgv_Tof8/?utm_source=ig_web_copy_link"

# Extract short code from URL
reel_shortcode = reel_url.split("/")[-2]

try:
    # Download the Reel
    loader.download_post(instaloader.Post.from_shortcode(loader.context, reel_shortcode), target="reels")
    print("Download successful! Check the 'reels' folder.")
except Exception as e:
    print("Error:", e)
