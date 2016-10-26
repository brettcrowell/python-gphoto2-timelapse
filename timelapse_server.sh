#!/bin/sh
# timelapse_server.sh

cd /home/pi/python-gphoto2-timelapse
. ./timelapse/bin/activate
nohup sudo -b python3 ./timelapse_server.py &
