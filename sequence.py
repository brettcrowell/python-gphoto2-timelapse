import time
from datetime import datetime

class Sequence:

    def __init__(self, exposures):
        self.exposures = exposures

    def by_ts(self, json):
        try:
            return int(json['ts'])
        except KeyError:
            return 0

    def add_image(self, image):
        self.exposures.push(image)

    def get_next_image(self, delay = 0):

        # sort exposures such that the furthest in the future come first
        self.exposures.sort(key=self.by_ts, reverse=True)

        # get the current time, in milliseconds
        current_ts = int(round(time.time() * 1000))

        while self.exposures:

            next_image = self.exposures.pop()
            next_image_ts = int(next_image['ts'])

            if((next_image_ts + delay) < current_ts):

                # skip any images that should have already been taken
                print('skipping image {} ({}, {})'.format(next_image['name'], next_image_ts, datetime.fromtimestamp(next_image_ts).strftime('{:%Y-%m-%d %H:%M:%S}')))

            else:

                # return the first image in the future that hasn't been
                return next_image

    def has_more_images(self):
        return len(self.exposures) > 0