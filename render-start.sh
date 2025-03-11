#!/bin/bash
echo "Installing Chrome..."
wget -q -O chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./chrome.deb
rm chrome.deb
echo "Chrome installed."

echo "Starting ReelXtract backend..."
gunicorn app:app
