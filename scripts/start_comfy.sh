#!/bin/bash

# ComfyUI Startup Script for nobara-laptop
# Auto-generated for AI Image Chat

echo "============================================"
echo "Starting ComfyUI for AI Image Chat"
echo "============================================"
echo ""

# Change to ComfyUI directory
cd /home/ant/AI/ComfyUI

# Activate conda environment
echo "Activating conda environment: comfy-env"
eval "$(conda shell.bash hook)"
conda activate comfy-env

# Check if activation worked
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate comfy-env"
    echo "Make sure conda is installed and comfy-env exists"
    exit 1
fi

echo "Environment activated successfully"
echo ""

# Start ComfyUI with optimized flags for 4090M
echo "Starting ComfyUI..."
echo "Access URLs:"
echo "  • Laptop: http://localhost:8188"
echo "  • Desktop: http://192.168.1.175:8188"
echo ""
echo "Press Ctrl+C to stop"
echo "============================================"
echo ""

python main.py \
    --listen \
    --cuda-malloc \
    --force-channels-last \
    --use-sage-attention \
    --dont-upcast-attention \
    --fast
