import json
from timelapse import GPhoto2Timelapse
from sequence import Sequence
from logger import Logger
from timelapse_errors import TimelapseError
from json.decoder import JSONDecodeError
import os

try:
    try:

        with open("saved_state.json") as saved_state:

            # if saved_state exists, use it to resume a previous lapse
            restored_state = json.load(saved_state)
            os.remove("saved_state.json")

            # make sure these are globals
            logr = Logger(restored_state["logs"])
            seq = Sequence(restored_state["exposures"], logr)
            lapse = GPhoto2Timelapse(seq, logr, restored_state["lapse"])

            logr.log("State restored from disk.  Here we go again!")

    except (FileNotFoundError, JSONDecodeError):

        with open("data.json") as data_file:

            # otherwise start a new one
            exposures = json.load(data_file)

            # make sure these are globals
            logr = Logger()
            seq = Sequence(exposures, logr)
            lapse = GPhoto2Timelapse(seq, logr)

            logr.log("New lapse started by `timelapse_server`")

    # and we're off!
    lapse.take_next_picture()

except FileNotFoundError as e:
    logr.log("no data.json file found in root directory (error: {})".format(e))

except JSONDecodeError:
    logr.log("malformed json found in root directory.  please ensure minimal format of [{ \"name\": \"\", \"ts\": 1474075839955 }")

except TimelapseError as e:

    logr.log("> Timelapse aborted, rebooting system.")

    outgoing_state = {
        "lapse": lapse.get_state(),
        "exposures": seq.get_exposures(),
        "logs": logr.get_log()
    }

    # write state to disk
    with open('saved_state.json', 'w') as outfile:
        json.dump(outgoing_state, outfile)