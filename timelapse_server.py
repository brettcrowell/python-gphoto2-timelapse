import json
from timelapse import Timelapse
from sequence import Sequence

with open("data.json") as data_file:
    exposures = json.load(data_file)

seq = Sequence(exposures)
lapse = Timelapse(seq)