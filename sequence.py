class Sequence:

    def __init__(self, exposures):
        self.exposures = exposures

    def get_next_image(self):
        return self.exposures.pop()