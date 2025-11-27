#!/bin/bash

# Exit on error
set -e

echo "Creating download directory..."
mkdir -p reels
chmod 777 reels

echo "Starting ReelXtract backend..."
exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120
