import time
from logger import Logger
from datetime import datetime


class DelaySequence:

    def __init__(self, delay_seconds, logger=Logger(), max_images=None, name="image"):
        self.delay_seconds = delay_seconds
        self.delay_ms = delay_seconds * 1000
        self.logger = logger
        self.image_count = 0
        self.max_images = max_images
        self.name = name

    def get_exposures(self):
        return []

    def get_next_image(self, delay=0):
        self.image_count += 1
        current_ts = int(round(time.time() * 1000))
        return {
            "name": self.name,
            "ts": current_ts + self.delay_ms
        }

    def has_more_images(self):
        if self.max_images is None:
            return True
        return self.image_count < self.max_images


class Sequence:

    exposures = []
    logger = None

    def __init__(self, exposures, logger = Logger()):
        self.exposures = exposures
        self.logger = logger

    def by_ts(self, json):
        try:
            return int(json['ts'])
        except KeyError:
            return 0

    def get_exposures(self):
        return self.exposures

    def add_image(self, image):
        self.exposures.append(image)

    def get_next_image(self, delay = 0):

        # sort exposures such that the furthest in the future come first
        self.exposures.sort(key=self.by_ts, reverse=True)

        # get the current time, in milliseconds
        current_ts = int(round(time.time() * 1000)) # @todo testing: 0

        while self.exposures:

            next_image = self.exposures.pop()
            next_image_ts = int(next_image['ts'])

            if((next_image_ts + delay) < current_ts):

                # skip any images that should have already been taken
                self.logger.log('Skipping image `{}-{}`, ({})'.format(next_image['name'],
                                                                      next_image_ts,
                                                                      datetime.fromtimestamp(
                                                                          next_image_ts / 1000).strftime(
                                                                          '%Y-%m-%d %H:%M:%S')))

            else:

                # return the first image in the future that hasn't been
                return next_image

    def has_more_images(self):
        return len(self.exposures) > 0
