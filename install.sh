#!/bin/bash

# Detect package type from /etc/issue
_found_arch() {
  local _ostype="$1"
  shift
  grep -qis "$*" /etc/issue && _OSTYPE="$_ostype"
}

# Detect package type
_OSTYPE_detect() {
  _found_arch PACMAN "Arch Linux" && return
  _found_arch DPKG   "Debian GNU/Linux" && return
  _found_arch DPKG   "Ubuntu" && return
  _found_arch YUM    "CentOS" && return
  _found_arch YUM    "Red Hat" && return
  _found_arch YUM    "Fedora" && return
  _found_arch ZYPPER "SUSE" && return

  [[ -z "$_OSTYPE" ]] || return

  if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Can't detect OS type from /etc/issue. Running fallback method."
  fi
  [[ -x "/usr/bin/pacman" ]]           && _OSTYPE="PACMAN" && return
  [[ -x "/usr/bin/apt-get" ]]          && _OSTYPE="DPKG" && return
  [[ -x "/usr/bin/yum" ]]              && _OSTYPE="YUM" && return
  [[ -x "/opt/local/bin/port" ]]       && _OSTYPE="MACPORTS" && return
  command -v brew >/dev/null           && _OSTYPE="HOMEBREW" && return
  [[ -x "/usr/bin/emerge" ]]           && _OSTYPE="PORTAGE" && return
  [[ -x "/usr/bin/zypper" ]]           && _OSTYPE="ZYPPER" && return
  if [[ -z "$_OSTYPE" ]]; then
    echo "No supported package manager installed on system"
    echo "(supported: apt, homebrew, pacman, portage, yum, zypper)"
    exit 1
  fi
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect OS type
_OSTYPE_detect

# Function to install packages based on detected OS type
install_package() {
    local package=$1
    case $_OSTYPE in
        PACMAN)
            sudo pacman -S --noconfirm $package
            ;;
        DPKG)
            sudo apt-get update
            sudo apt-get install -y $package
            ;;
        YUM)
            sudo yum install -y $package
            ;;
        ZYPPER)
            sudo zypper install -y $package
            ;;
        MACPORTS)
            sudo port install $package
            ;;
        HOMEBREW)
            brew install $package
            ;;
        PORTAGE)
            sudo emerge $package
            ;;
        *)
            echo "Unsupported package manager"
            exit 1
            ;;
    esac
}

# Check and Install Docker
if ! command_exists docker; then
    echo "Docker not found. Installing Docker..."
    case $_OSTYPE in
        DPKG)
            sudo apt-get update
            sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
            sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
            sudo apt-get update
            sudo apt-get install -y docker-ce
            ;;
        *)
            install_package docker
            ;;
    esac
    sudo usermod -aG docker $USER
    newgrp docker
    sudo systemctl start docker
    sudo systemctl enable docker
    echo "Docker installed successfully."
else
    echo "Docker is already installed."
fi

# Check and Install Python
if ! command_exists python3; then
    echo "Python3 not found. Installing Python..."
    install_package python3
    echo "Python3 installed successfully."
else
    echo "Python3 is already installed."
fi

# Check and Install pip
if ! command_exists pip3; then
    echo "pip3 not found. Installing pip..."
    case $_OSTYPE in
        DPKG)
            sudo apt-get update
            sudo apt-get install -y python3-pip
            ;;
        *)
            install_package python3-pip
            ;;
    esac
    echo "pip3 installed successfully."
else
    echo "pip3 is already installed."
fi

# Install Python Packages
echo "Installing required Python packages..."
pip3 install "python-socketio[Server]" flask eventlet geocoder

echo "Script execution completed."
