#!/usr/bin/env bash

apt-get update
apt-get install certbot
apt -y install python-certbot-nginx

# I *think* this is needed
sudo pip3 -vvv install --upgrade --force-reinstall cffi
