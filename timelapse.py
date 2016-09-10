import time

class Timelapse:

    sequence = None
    preferences = {}

    deferredImage = None

    def __init__(self, sequence, max_ms_between_images = 3600000, min_image_kb = 100000):

        self.sequence = sequence
        self.preferences['max_ms_between_images'] = max_ms_between_images
        self.preferences['min_image_kb'] = min_image_kb

        # and we're off!
        self.take_next_picture()

    def reset_usb(self, reason, callback):
        return None

    def connect_to_camera(self, callback):
        return None

    def take_picture(self, image):
        print(image)
        return None

    def upload_to_s3(self, imagePath, bucket, key, recurse):
        return None

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
            self.take_picture(next_image)

        else:
            print("done")