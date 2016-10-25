#!/bin/sh
# timelapse_server.sh

cd ~/python-gphoto2-timelapse
source timelapse/bin/activate
nohup sudo -b python3 timelapse_server.py &