#!/bin/bash
# Quick wrapper to post news manually to Facebook
# Usage: ./post_manually.sh [count]
# Example: ./post_manually.sh 5

cd "$(dirname "$0")/nepalpulse"

count=${1:-5}

echo "🚀 Starting manual Facebook post generator..."
echo "📋 Each post will be copied to your clipboard"
echo "📌 You paste into Facebook, then confirm here"
echo ""

python3 copy_post_to_clipboard.py "$count"
