import json
from gphoto2_timelapse import GPhoto2Timelapse
from sequence import Sequence

with open("data.json") as data_file:
    exposures = json.load(data_file)

seq = Sequence(exposures)
lapse = GPhoto2Timelapse(seq)