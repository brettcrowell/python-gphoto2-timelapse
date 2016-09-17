import json
from timelapse import GPhoto2Timelapse
from sequence import Sequence
from logger import Logger

with open("data.json") as data_file:
    exposures = json.load(data_file)

logger = Logger()
seq = Sequence(exposures, logger)
#lapse = WebcamTimelapse(seq)
lapse = GPhoto2Timelapse(seq, logger)