#!/bin/bash

# Exit on error
set -e

echo "Installing Chrome dependencies..."
sudo apt-get update
sudo apt-get install -y wget gnupg2

echo "Adding Chrome repository..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google.list

echo "Installing Chrome..."
sudo apt-get update
sudo apt-get install -y google-chrome-stable
echo "Chrome installed successfully."

echo "Creating download directory..."
mkdir -p reels
chmod 777 reels

echo "Starting ReelXtract backend..."
exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120
