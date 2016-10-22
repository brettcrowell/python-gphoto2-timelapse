This project allows users to run clock-time based timelapses using Python, gPhoto2, and was designed specifically to run headless on a Raspberry Pi.

## Recommended Hardware

- Raspberry Pi (CanaKit's RPi3 Model B Kit is recommended) with MicroSD Card & Raspbian installed
- DLI Iot Relay & 2 male-female DuPont/jumper wires
- gPhoto2 Compatible Camera with Power Adapter & USB (ex. Nikon CoolPix S3300, UC-E6 USB cable & EH-62G AC Adapter)

### Other Recommendations

- Fat Gecko Mini Camera and Camcorder Mount
- JOBY GorillaPod

## Dependencies & Basic Installation

This package relies heavily on external software. Below you'll find a crash course to get your Pi up and running. Most other machines should come up by following similar steps.

1) Ensure that Python 3 and PIP3 are installed

2) Install gPhoto2 using the gPhoto2 Updater (https://github.com/gonzalo/gphoto2-updater)

```
$ wget https://raw.githubusercontent.com/gonzalo/gphoto2-updater/master/gphoto2-updater.sh && chmod +x gphoto2-updater.sh && sudo ./gphoto2-updater.sh
```

3) Clone this repo...

```
cd ~/
git clone git@github.com:brettcrowell/python-gphoto2-timelapse.git
```

4) Install Python dependencies

```
pip3 install -r requirements.txt
```

## Hardware Setup

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

## Usage

### Pre-Defining a Sequence

As mentioned above, this package allows you to create timelapses based on clock-time.  As such, the input to the application should be a list of UTC timestamps (surrounded by some meta-data) that looks roughly like this...

```
[
    {
      name: 'sunrise',
      bucket: 'bcrowell-timelapse',
      ts: 1425380400000
    }
]
```

By default, this list will be stored in a file called `data.json`

_Note: If bucket is omitted, no attempt will be made to upload to S3, and images will be stored in the ./output directory._

### Creating a custom Sequene in Javascript

In the `./samples` directory, you'll find a few Javascript files that illustrate how to create JSON Sequences in Node.  To run them (and create a new `data.json` file)...

```
node ./samples/simple-sample.js &> data.json
```

### Running the Lapse

```
sudo python3 timelapse_server.py
```

_Why `sudo``?  During the course of the lapse, we may attempt to virtually re-seat the camera's USB conneection.  To do this, we must delete a system file with `sudo` permissions_


## Incomplete Webcam stuff...

brew install cmake
install opencv...
http://www.pyimagesearch.com/2015/06/29/install-opencv-3-0-and-python-3-4-on-osx/

git checkout 3.1.0

>>> import site; site.getsitepackages()
['/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages', '/Library/Python/3.5/site-packages']

```