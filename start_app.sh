#!/bin/bash

# AI Image Chat - Quick Start Script

echo "============================================"
echo "AI Image Chat - Starting..."
echo "============================================"
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "ERROR: app.py not found!"
    echo "Please run this script from the ai-image-chat directory"
    exit 1
fi

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "ERROR: Python not found!"
    echo "Please install Python 3.10 or later"
    exit 1
fi

echo "Starting AI Image Chat..."
echo ""
echo "Access URLs:"
echo "  • Laptop: http://localhost:7860"
echo "  • Desktop: http://192.168.1.175:7860"
echo ""
echo "Press Ctrl+C to stop"
echo "============================================"
echo ""

python app.py
