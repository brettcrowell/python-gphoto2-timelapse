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

    def get_next_image(self):

        # sort exposures such that the furthest in the future come first
        self.exposures.sort(key=self.by_ts, reverse=True)

        # return the first image that is in the future
        return self.exposures.pop()