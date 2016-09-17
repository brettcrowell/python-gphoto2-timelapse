import time
import os
import threading
import signal
import gphoto2 as gp
from subprocess import call
from logger import Logger
from timelapse_errors import TimeoutError, TimelapseError

class Timelapse:
    
    sequence = None
    logger = None
    
    state = {
        "preferences": {
            "max_ms_between_images": 600000,
            "max_ms_image_capture": 60000,
            "min_image_kb": 100000,
            "location": os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        },
        "failed_image": None,
        "deferred_image": None
    }

    def __init__(self, sequence, logger = Logger(), initial_state = None):

        self.sequence = sequence
        self.logger = logger

        if(initial_state):
            self.state = initial_state

        # make sure the output and log directories exist @todo log directory
        if not os.path.exists(os.path.join(self.state['preferences']['location'], 'output')):
            os.makedirs(os.path.join(self.state['preferences']['location'], 'output'))

    def get_state(self):
        return self.state

    def destruct(self, image):
        self.state['failed_image'] = image
        raise TimelapseError

    def reset_usb(self, image):
        self.logger.log("-- Resetting USB")
        self.state['failed_image'] = image
        return None

    def killall_ptp(self, image):
        self.logger.log("-- Killing PTPCamera")
        self.state['failed_image'] = image
        call(["killall", "PTPCamera"])

    def take_picture(self, image):
        raise NotImplementedError

    def upload_to_s3(self, image_path, image):
        return None

    def take_next_picture(self, delay = 0):

        next_image = None

        if self.state['failed_image']:

            # if an image failed to capture, try it again
            next_image = self.state['failed_image']
            self.state['failed_image'] = None

        elif self.state['deferred_image']:

            # images may be deferred if they would have caused the camera to idle for too long
            next_image = self.state['deferred_image']
            self.state['deferred_image'] = None

        else:

            # standard lookup for next image
            if (self.sequence.has_more_images()):
                next_image = self.sequence.get_next_image(delay)

        if next_image:

            # determine how long we need to wait
            current_ts = int(round(time.time() * 1000))
            max_ms_between_images = self.state['preferences']['max_ms_between_images']
            ms_until_next_image = next_image['ts'] - current_ts

            if(ms_until_next_image > max_ms_between_images):

                # some cameras have been known to 'drop off' if they aren't accessed frequently enough.
                # the following provision will take a throwaway image every (default 60 mins) to prevent that.

                self.state['deferred_image'] = next_image

                next_image = {
                    'name': 'keep-alive-signal',
                    'ts': current_ts + max_ms_between_images,
                    'discard': True
                }

                # re-calculate the timer variable, as the image has changed
                ms_until_next_image = max_ms_between_images

            # how many seconds until we shoot again?  min should be 0s
            sec_until_next_image = max(ms_until_next_image / 1000, 0)

            self.logger.log("Next image (`{}-{}`) will be taken in {} seconds".format(next_image['name'],
                                                                            next_image['ts'],
                                                                            sec_until_next_image))

            # and now, we wait (gotta love synchronous code)
            time.sleep(sec_until_next_image)

            try:

                # don't let the capture function die on us
                ms_capture_timeout = self.state['preferences']['max_ms_image_capture']
                sec_capture_timeout = int(ms_capture_timeout / 1000)

                # at long last, the next_image's time has arrived.  capture!
                with timeout(seconds=sec_capture_timeout):
                    image_path = self.take_picture(next_image)

                if ('bucket' in next_image):

                    # asynchronously upload this image to s3 if there is a bucket specified
                    amazon_upload_thread = threading.Thread(target=self.upload_to_s3, args=(image_path, next_image))
                    amazon_upload_thread.start()

            except TimeoutError as ex:
                self.logger.log("Image (`{}-{}`) failed to capture in {}s.  Aborting.".format(next_image['name'],
                                                                                    next_image['ts'],
                                                                                    sec_capture_timeout))
                self.destruct(next_image)

            # calculate how far behind schedule we are
            current_ts = int(round(time.time() * 1000))
            ms_image_delay = current_ts - next_image['ts']

            self.logger.log("Capture complete (main thread blocked for {}s)".format(ms_image_delay / 1000))

            # recurse
            self.take_next_picture(ms_image_delay)

        else:
            self.logger.log("done")

class GPhoto2Timelapse(Timelapse):

    def take_picture(self, image):

        image_filename = "{}-{}".format(image['name'], image['ts'])

        self.logger.log("Capturing image `{}`".format(image_filename))

        context = gp.gp_context_new()
        camera = gp.check_result(gp.gp_camera_new())
        target = None

        try:

            # initialize the camera
            gp.check_result(gp.gp_camera_init(camera, context))

            # save information about found camera
            # print(gp.check_result(gp.gp_camera_get_summary(camera, context)))

            # capture image, making note of the file path on memory card
            file_path = gp.check_result(gp.gp_camera_capture(camera, gp.GP_CAPTURE_IMAGE, context))

            self.logger.log('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))

            # get reference to image file on camera
            camera_file = gp.check_result(gp.gp_camera_file_get(camera,
                                                                file_path.folder,
                                                                file_path.name,
                                                                gp.GP_FILE_TYPE_NORMAL,
                                                                context))

            # determine where to store this file locally
            target = os.path.join(self.preferences['location'], "output", "{}.jpg".format(image_filename))

            self.logger.log('Copying image to {}'.format(target))

            # download image to directory determined above
            gp.check_result(gp.gp_file_save(camera_file, target))

            # @todo need to check file size here

        except gp.GPhoto2Error as ex:

            if ex.code == gp.GP_ERROR_MODEL_NOT_FOUND:
                self.logger.log("Unable to find usable camera.  Is it connected, alive, and awake? ({})".format(ex.string))
                self.destruct(image)

            elif ex.code == gp.GP_ERROR_IO_USB_CLAIM:
                self.logger.log("Camera is already in use.  If on Mac, try running `sudo killall PTPCamera` ({})".format(ex.string))
                self.killall_ptp(image)

            elif ex.code == gp.GP_ERROR_IO:
                self.logger.log("I/O issue with camera, USB connection needs to be reset ({})".format(ex.string))
                self.reset_usb(image)

            else:
                self.logger.log("GPhoto2 Error: {}".format(ex.string))
                self.destruct(image)

        finally:

            # let go of the camera now
            gp.check_result(gp.gp_camera_exit(camera, context))

        return target

class WebcamTimelapse(Timelapse):

    def take_picture(self, image):
        return None

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