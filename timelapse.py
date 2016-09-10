class Timelapse:

    def __init__(self, sequence):
        self.sequence = sequence
        print(self.sequence.get_next_image())