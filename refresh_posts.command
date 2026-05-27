#!/bin/bash
# Double-click this file in Finder to refresh the posts/ folder.
# Use when the daemon is down and you need fresh posts to copy-paste.

cd "$(dirname "$0")/nepalpulse"
python3 posts_folder.py

echo ""
echo "Press any key to close this window..."
read -n 1
