#!/usr/bin/env bash

# Update source repository so that it includes python3.10
sudo apt update && sudo apt upgrade -y
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa

# Install Python3.10
sudo apt install python3.10

# Set 3.10 as the default, instead of 3.8
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 2
sudo update-alternatives --config python3

# Fix python3-apt, pip and distutils
sudo apt remove --purge python3-apt
sudo apt autoclean
sudo apt install python3-apt
sudo apt install python3.10-distutils

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python3.10 get-pip.py

sudo apt install python3.10-venv python3.10-dev
