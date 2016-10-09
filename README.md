## Dependencies

This software depends on a few open soure packages including...

- gPhoto2

To install dependencies...

```
gphoto2 updater...
```

(link)

Python dependencies...

```
apt-get install python3
apt-get install python3-pip
pip3 install gphoto2
```

## Creating Sequences

Though the timelapse itself has no dependency on Node, the sample sequence generators are written with Javascipt.
Therefore, to use them, ensure you have `nvm` installed...

```
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.32.0/install.sh | bash
```

To run them with the latest Node version...

```
cd ~/git/python-gphoto2-timelapse/
nvm use stable
node ./samples/simple-sample.js &> data.json
```

## Starting the Lapse

```
sudo python3 timelapse_server.py
```

_Why `sudo``?  During the course of the lapse, we may attempt to virtually re-seat the camera's USB conneection.
To do this, we must delete a system file with `sudo` permissions_

## Incomplete Webcam stuff...

brew install cmake
install opencv...
http://www.pyimagesearch.com/2015/06/29/install-opencv-3-0-and-python-3-4-on-osx/

git checkout 3.1.0

>>> import site; site.getsitepackages()
['/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages', '/Library/Python/3.5/site-packages']

```