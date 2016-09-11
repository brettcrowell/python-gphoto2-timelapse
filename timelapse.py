import time
import gphoto2 as gp
import os
import subprocess

class Timelapse:

    sequence = None
    preferences = {}

    deferredImage = None

    def __init__(self, sequence, max_ms_between_images = 3600000, min_image_kb = 100000):

        self.sequence = sequence
        self.preferences['max_ms_between_images'] = max_ms_between_images
        self.preferences['min_image_kb'] = min_image_kb
        self.preferences['location'] = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

        # make sure the output and log directories exist @todo log directory
        if not os.path.exists(os.path.join(self.preferences['location'], 'output')):
            os.makedirs(os.path.join(self.preferences['location'], 'output'))

        # and we're off!
        self.take_next_picture()

    def reset_usb(self, reason, callback):
        return None

    def connect_to_camera(self, callback):
        return None

    def take_picture(self, image):

        if(False):
            # if the camera isn't connected, go looking for it
            print("no camera found")
        else:

            print("capturing image {} ({})".format(image['name'], image['ts']))

            context = gp.gp_context_new()
            camera = gp.check_result(gp.gp_camera_new())

            try:

                # initialize the camera
                gp.check_result(gp.gp_camera_init(camera, context))

                # save information about found camera
                # gp.check_result(gp.gp_camera_get_summary(camera, context))

                # capture image, making note of the file path on memory card
                file_path = gp.check_result(gp.gp_camera_capture(camera, gp.GP_CAPTURE_IMAGE, context))

                print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))

                # get reference to image file on camera
                camera_file = gp.check_result(
                    gp.gp_camera_file_get(camera, file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL, context))

                # determine where to store this file locally
                target = os.path.join(self.preferences['location'], "output", "{}{}.jpg".format(image['name'], image['ts']))

                print('Copying image to', target)

                # download image to directory determined above
                gp.check_result(gp.gp_file_save(camera_file, target))

            except gp.GPhoto2Error as ex:

                if ex.code == gp.GP_ERROR_MODEL_NOT_FOUND:
                    print("Unable to find usable camera.  Is it connected, alive, and awake? ({})".format(ex.string))

                elif ex.code == gp.GP_ERROR_IO_USB_CLAIM:
                    print("Camera is already in use.  If on Mac, try running `sudo killall PTPCamera` ({})".format(ex.string))

                else:
                    print("GPhoto2 Error: {}".format(ex.string))

            gp.check_result(gp.gp_camera_exit(camera, context))

            # continue with rest of program

            current_ts = image['ts']  # int(round(time.time() * 1000))
            ms_image_delay = current_ts - image['ts']

            print("current image has processed {}s behind scheduled time".format(ms_image_delay / 1000))

            self.take_next_picture(ms_image_delay)

        # this function should have saved the captured image to disk.  return the path
        return target or None

    def upload_to_s3(self, image_path, image):
        print("Uploading {} to S3".format(image_path))

    def take_next_picture(self, delay = 0):

        if(self.sequence.has_more_images()):

            current_ts = 0  # int(round(time.time() * 1000))

            # images may be deferred if they would have caused the camera to idle for too long
            next_image = self.deferredImage or self.sequence.get_next_image(delay)

            ms_until_next_image = next_image['ts'] - current_ts

            if(ms_until_next_image > self.preferences['max_ms_between_images']):

                # some cameras have been known to 'drop off' if they aren't accessed frequently enough.
                # the following provision will take a throwaway image every (default 60 mins) to prevent that.

                self.deferredImage = next_image

                next_image = {
                    'name': 'keep-alive-signal',
                    'ts': current_ts + self.preferences['max_ms_between_images'],
                    'discard': True
                }

                # re-caclculate the timer variable, as the image has changed
                ms_until_next_image = self.preferences['max_ms_between_images']

            else:

                # back on track, so reset the cycle
                self.deferredImage = None

            # and now, we wait (gotta love synchronous code)
            time.sleep(ms_until_next_image / 1000)

            # after waking up
            image_path = self.take_picture(next_image)

            if next_image['bucket']:
                self.upload_to_s3(image_path, next_image)

        else:
            print("done")