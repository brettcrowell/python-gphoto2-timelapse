import time
import gphoto2 as gp
import os
import threading
import signal

class Timelapse:

    sequence = None
    preferences = {}

    deferredImage = None

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

    def reset_usb(self, reason, callback):
        return None

    def take_picture(self, image):

        image_filename = "{}-{}".format(image['name'], image['ts'])

        print("Capturing image `{}`".format(image_filename))

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

            print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))

            # get reference to image file on camera
            camera_file = gp.check_result(gp.gp_camera_file_get(camera,
                                                                file_path.folder,
                                                                file_path.name,
                                                                gp.GP_FILE_TYPE_NORMAL,
                                                                context))

            # determine where to store this file locally
            target = os.path.join(self.preferences['location'], "output", "{}.jpg".format(image_filename))

            print('Copying image to', target)

            # download image to directory determined above
            gp.check_result(gp.gp_file_save(camera_file, target))

            # @todo need to check file size here

        except gp.GPhoto2Error as ex:

            if ex.code == gp.GP_ERROR_MODEL_NOT_FOUND:
                print("Unable to find usable camera.  Is it connected, alive, and awake? ({})".format(ex.string))

            elif ex.code == gp.GP_ERROR_IO_USB_CLAIM:
                print("Camera is already in use.  If on Mac, try running `sudo killall PTPCamera` ({})".format(ex.string))

            elif ex.code == gp.GP_ERROR_IO:
                print ("I/O issue with camera, USB connection needs to be reset ({})".format(ex.string))

            else:
                print("GPhoto2 Error: {}".format(ex.string))

        finally:

            # let go of the camera now
            gp.check_result(gp.gp_camera_exit(camera, context))

        return target

    def upload_to_s3(self, image_path, image):
        return None

    def take_next_picture(self, delay = 0):

        if(self.sequence.has_more_images()):

            current_ts = int(round(time.time() * 1000)) # @todo testing: 0

            # images may be deferred if they would have caused the camera to idle for too long
            next_image = self.deferredImage or self.sequence.get_next_image(delay)

            max_ms_between_images = self.preferences['max_ms_between_images']
            ms_until_next_image = next_image['ts'] - current_ts

            if(ms_until_next_image > max_ms_between_images):

                # some cameras have been known to 'drop off' if they aren't accessed frequently enough.
                # the following provision will take a throwaway image every (default 60 mins) to prevent that.

                self.deferredImage = next_image

                next_image = {
                    'name': 'keep-alive-signal',
                    'ts': current_ts + max_ms_between_images,
                    'discard': True
                }

                # re-calculate the timer variable, as the image has changed
                ms_until_next_image = max_ms_between_images

            else:

                # back on track, so reset the cycle
                self.deferredImage = None

            # how many seconds until we shoot again?
            sec_until_next_image = ms_until_next_image / 1000

            print("Next image (`{}-{}`) will be taken in {} seconds".format(next_image['name'],
                                                                            next_image['ts'],
                                                                            sec_until_next_image))

            # and now, we wait (gotta love synchronous code)
            time.sleep(sec_until_next_image)

            try:

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