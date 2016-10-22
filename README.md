This project allows users to run clock-time based timelapses using Python, gPhoto2, and was designed specifically to run headless on a Raspberry Pi.

## Recommended Hardware

* Computer capable of running Python 3 & gPhoto2
  * CanaKit's RPi3 Model B Kit with Raspbian recommended
* A/C Power Relay
  * Digital Loggers IoT Relay recommended
  * 2 male-female DuPont/jumper wires also required
* gPhoto2 Compatible Camera with Power Adapter & USB Cable
  * Tested with Canon 6D and Nikon CoolPix S3300
  * For Nikon, UC-E6 USB cable & EH-62G A/C Adapter required

### Other Recommendations

- Fat Gecko Mini Camera and Camcorder Mount
- JOBY GorillaPod

## Dependencies & Basic Installation

### Hardware Setup

- Plug your RPi and IoT Relay into separate wall outlets (same recepticle is fine)
- Plug your Camera into a "Normally On" outlet on the relay
- Connect your camera's USB output to the RPi
- Install Jumper wires between the RPi's GPIO pins and the IoT Relay (see next section)

#### Relay Setup for Power Toggle

If your camera becomes unresponsive during the lapse, we'll use the IoT Relay to unplug it and plug it back in.  Specifically, we'll configure the relay such that power is *normally on*.  If the camera fails, we'll activate a signal on the RPi's GPIO pin.  When that signal is hot, the relay will switch *off*.  Once we deactivate the signal, the relay will switch back *on* again and we'll wait a few seconds for the camera to boot.

- Plug the signal/hot wire into BCM Pin #3 (RPi Pin #5)
- Plug the ground wire into RPi Pin #6 (Ground)
- Matching Hot to (+) and Ground to (-), plug jumpers into the relay
- Ensure that the camera power adapter is seated in a "Normally On" outlet

Learn more about the pins on your Raspberry Pi here...

* http://pinout.xyz/pinout/pin5_gpio3
* https://learn.sparkfun.com/tutorials/raspberry-gpio/python-rpigpio-example

### Software Setup

This package relies heavily on external software. Below you'll find a crash course to get your Pi up and running. Most other machines should come up by following similar steps.

1) Ensure that Python 3 and PIP3 are installed

2) Install gPhoto2 using the gPhoto2 Updater (https://github.com/gonzalo/gphoto2-updater)

```
wget https://raw.githubusercontent.com/gonzalo/gphoto2-updater/master/gphoto2-updater.sh && chmod +x gphoto2-updater.sh && sudo ./gphoto2-updater.sh
```

3) Clone this repo...

```
cd ~/
git clone git@github.com:brettcrowell/python-gphoto2-timelapse.git
```

4) Create a new Python Virtual Environment to isolate this app from your overall environment...

```
cd ~/python-gphoto2-timelapse
sudo pip3 install virtualenv
virtualenv timelapse
source timelapse/bin/activate
```

5) Install Python dependencies

```
sudo pip3 install -r requirements.txt
```

_Why `sudo``?  During the course of the lapse, we may attempt to virtually re-seat the camera's USB conneection.  To do this, we must delete a system file with `sudo` permissions_

## Creating Sequences

Though the timelapse itself has no dependency on Node, the sample sequence generators are written with Javascipt.  Therefore, to use them, ensure you have `nvm` installed...

```
curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
sudo apt install -y nodejs
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

## Incomplete Webcam stuff...

brew install cmake
install opencv...
http://www.pyimagesearch.com/2015/06/29/install-opencv-3-0-and-python-3-4-on-osx/

git checkout 3.1.0

>>> import site; site.getsitepackages()
['/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages', '/Library/Python/3.5/site-packages']

```
