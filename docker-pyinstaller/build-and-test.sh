#!/bin/bash

if [ -z "$1" ]; then
    echo "Enter Dockerfile name"
    exit 1
fi

if ! command -v docker &>/dev/null && ! command -v podman &>/dev/null; then
    echo "Neither Docker nor Podman is installed"
    exit 1
fi

# Prompt for the image name (container name)
read -p "Enter container name (e.g., pyinstaller-linux, pyinstaller-windows, pyinstaller-osx): " name

# Prepend the repository name to form the full image name
image_name="darkavengerreborn/$name"

# Set the default platforms depending on the name
if [[ "$name" == *"linux"* ]]; then
    platforms="linux/amd64"  # For Linux targets, use multiple platforms
else
    platforms="linux/amd64"  # For non-Linux targets, default to amd64
fi

build_and_run() {
    local build_cmd=$1
    local run_cmd=$2
    local dockerfile=$3
    local pyinstaller_args=${4:-"--onefile"}

    # Check if docker buildx is available
    if command -v docker &>/dev/null && docker buildx version &>/dev/null; then
        # Use buildx for multi-architecture builds
        $build_cmd buildx create --use  # Initialize buildx builder
        $build_cmd buildx build --platform "$platforms" -f "$dockerfile" -t "$image_name" . --push && \
        $run_cmd -v "$(pwd)/test:/src/" "$image_name" "pyinstaller main.py $pyinstaller_args"
    else
        # Fallback to standard docker build for a single architecture
        $build_cmd -f "$dockerfile" -t "$image_name" . && \
        $run_cmd -v "$(pwd)/test:/src/" "$image_name" "pyinstaller main.py $pyinstaller_args"
    fi
}

# Try Docker first, then Podman if it fails
if ! build_and_run "docker" "docker run" "$1"; then
    echo "Docker build failed, trying Podman..."
    build_and_run "podman" "podman run" "$1"
fi
