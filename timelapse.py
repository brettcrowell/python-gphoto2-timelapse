import time
import os
import threading
import signal
from subprocess import call

class Timelapse:

    sequence = None
    preferences = {}

    # if an image fails to capture, it should be re-introduced after any reboot/etc.
    failed_image = None

    # if the next image is to be taken too far in the future (> max_ms_between_images), it needs to
    # be deferred so we can insert a keep-alive-signal image
    deferred_image = None

    def __init__(self, sequence, max_ms_between_images = 600000, max_ms_image_capture=60000, min_image_kb = 100000):

        self.sequence = sequence

        # general preferences
        self.preferences['max_ms_between_images'] = max_ms_between_images
        self.preferences['max_ms_image_capture'] = max_ms_image_capture
        self.preferences['min_image_kb'] = min_image_kb
        self.preferences['location'] = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

        # make sure the output and log directories exist @todo log directory
        if not os.path.exists(os.path.join(self.preferences['location'], 'output')):
            os.makedirs(os.path.join(self.preferences['location'], 'output'))

        # and we're off!
        self.take_next_picture()

    def write_timelapse_meta_to_disk(self):
        return None

    def reboot_machine(self, image):
        print("-- Rebooting Machine")
        self.failed_image = image
        return None

    def reset_usb(self, image):
        print("-- Resetting USB")
        self.failed_image = image
        return None

    def killall_ptp(self, image):
        print("-- Killing PTPCamera")
        self.failed_image = image
        call(["killall", "PTPCamera"])

    def take_picture(self, image):
        raise NotImplementedError

    def upload_to_s3(self, image_path, image):
        return None

    def take_next_picture(self, delay = 0):

        next_image = None

        if self.failed_image:

            # if an image failed to capture, try it again
            next_image = self.failed_image
            self.failed_image = None

        elif self.deferred_image:

            # images may be deferred if they would have caused the camera to idle for too long
            next_image = self.deferred_image
            self.deferred_image = None

        else:

            # standard lookup for next image
            if (self.sequence.has_more_images()):
                next_image = self.sequence.get_next_image(delay)

        if next_image:

            # determine how long we need to wait
            current_ts = int(round(time.time() * 1000))
            max_ms_between_images = self.preferences['max_ms_between_images']
            ms_until_next_image = next_image['ts'] - current_ts

            if(ms_until_next_image > max_ms_between_images):

                # some cameras have been known to 'drop off' if they aren't accessed frequently enough.
                # the following provision will take a throwaway image every (default 60 mins) to prevent that.

                self.deferred_image = next_image

                next_image = {
                    'name': 'keep-alive-signal',
                    'ts': current_ts + max_ms_between_images,
                    'discard': True
                }

                # re-calculate the timer variable, as the image has changed
                ms_until_next_image = max_ms_between_images

            # how many seconds until we shoot again?  min should be 0s
            sec_until_next_image = max(ms_until_next_image / 1000, 0)

            print("Next image (`{}-{}`) will be taken in {} seconds".format(next_image['name'],
                                                                            next_image['ts'],
                                                                            sec_until_next_image))

            # and now, we wait (gotta love synchronous code)
            time.sleep(sec_until_next_image)

            try:

                # don't let the capture function die on us
                ms_capture_timeout = self.preferences['max_ms_image_capture']
                sec_capture_timeout = int(ms_capture_timeout / 1000)

                # at long last, the next_image's time has arrived.  capture!
                with timeout(seconds=sec_capture_timeout):
                    image_path = self.take_picture(next_image)

                if ('bucket' in next_image):

                    # asynchronously upload this image to s3 if there is a bucket specified
                    amazon_upload_thread = threading.Thread(target=self.upload_to_s3, args=(image_path, next_image))
                    amazon_upload_thread.start()

            except TimeoutError as ex:
                print("Image (`{}-{}`) failed to capture in {}s.  Aborting.".format(next_image['name'],
                                                                                    next_image['ts'],
                                                                                    sec_capture_timeout))
                self.reboot_machine(next_image)

            # calculate how far behind schedule we are
            current_ts = int(round(time.time() * 1000))
            ms_image_delay = current_ts - next_image['ts']

            print("Capture complete (main thread blocked for {}s)".format(ms_image_delay / 1000))

            # recurse
            self.take_next_picture(ms_image_delay)

        else:
            print("done")

class TimeoutError(Exception):
    pass

class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)