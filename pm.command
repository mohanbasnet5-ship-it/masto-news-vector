#!/bin/bash
# Double-click this in Finder to see NepalPulse project status.
cd "$(dirname "$0")"
python3 pm.py
echo ""
echo "Press any key to close..."
read -n 1
