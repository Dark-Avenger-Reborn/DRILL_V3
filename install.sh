#!/bin/bash

## Check and Install Dependencies

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

### Check and Install Docker
if ! command_exists docker; then
    echo "Docker not found. Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    sudo apt-get update
    sudo apt-get install -y docker-ce
    sudo systemctl start docker
    sudo systemctl enable docker
    echo "Docker installed successfully."
else
    echo "Docker is already installed."
fi

### Check and Install Python
if ! command_exists python3; then
    echo "Python3 not found. Installing Python..."
    sudo apt-get update
    sudo apt-get install -y python3
    echo "Python3 installed successfully."
else
    echo "Python3 is already installed."
fi

### Check and Install pip
if ! command_exists pip3; then
    echo "pip3 not found. Installing pip..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
    echo "pip3 installed successfully."
else
    echo "pip3 is already installed."
fi

## Install Python Packages
echo "Installing required Python packages..."
pip3 install python-socketio flask eventlet

echo "Script execution completed."
