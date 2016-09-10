class Sequence:

    def __init__(self, json_path):
        self.exposures = [1]

    def get_next_image(self):
        return self.exposures.pop()