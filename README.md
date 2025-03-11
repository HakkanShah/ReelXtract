# ReelXtract – Instagram Reels Downloader

ReelXtract is a simple and fast tool to download Instagram Reels instantly. Just paste the Reel URL, click download, and save the video with a sleek Instagram-themed UI.

## Features

- One-click download of Instagram Reels
- Fast & secure backend using Flask and Instaloader
- Beautiful, responsive Instagram-themed UI
- Rate limiting to prevent abuse
- Deployed on GitHub Pages (frontend) and Render (backend)

## Live Demo

- **Frontend:** [https://hakkanshah.github.io/ReelXtract/](https://hakkanshah.github.io/ReelXtract/)
- **Backend:** Deployed on Render

# Installation

## Prerequisites
- Python 3.x
- pip

## Steps
1. Clone the repository:
   git clone https://github.com/HakkanShah/ReelXtract.git
   **cd ReelXtract**
2. Install the dependencies:
   **pip install -r requirements.txt**
3. Run the Flask backend:
   **python app.py**
4. Open **index.html** in your browser to use the tool.

# Deployment

### GitHub Pages (Frontend)
The frontend is deployed on GitHub Pages at: https://hakkanshah.github.io/ReelXtract/

### Render (Backend)
The backend is deployed on Render using the start command:
gunicorn app:app

# Troubleshooting
 - **Rate Limiting:** The app limits requests to 5 per minute on the `/download` endpoint. Adjust limits if necessary.  
- **Instagram API Changes:** If Instaloader stops working, check for updates or review the logs in `error.log`.  
- **Logging:** Errors are logged to `error.log` for debugging purposes.  

# Contributing
Contributions, issues, and feature requests are welcome! Feel free to fork the repo and submit a pull request. Please see the issues page for more details.
   
