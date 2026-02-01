#!/usr/bin/env python3

import argparse
import json
import os

from timelapse import GPhoto2Timelapse
from sequence import Sequence, DelaySequence
from logger import Logger
from timelapse_errors import TimelapseError

parser = argparse.ArgumentParser(description="Run a clock-time based timelapse")
parser.add_argument("--file", help="JSON file containing exposure sequence")
parser.add_argument("--delay", type=int, help="Fixed delay in seconds between exposures (runs indefinitely)")
args = parser.parse_args()

# default: capture 24 hours into 1 minute at 30fps → 1800 frames over 86400s → 48s delay
DEFAULT_DELAY = 48

def save_state_to_disk(filename):

    outgoing_state = {
        "lapse": lapse.get_state(),
        "exposures": seq.get_exposures(),
        "logs": logr.get_log()
    }

    # write state to disk
    with open(filename, 'w') as outfile:
        json.dump(outgoing_state, outfile)

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

    except (OSError, ValueError):

        logr = Logger()

        if args.file:
            # load exposures from file
            with open(args.file) as data_file:
                exposures = json.load(data_file)
            seq = Sequence(exposures, logr)
            logr.log("New lapse started by `timelapse_server`")
        else:
            # run indefinitely with fixed delay between exposures
            delay = args.delay or DEFAULT_DELAY
            seq = DelaySequence(delay, logr)
            logr.log("New lapse started with {}s delay".format(delay))

        lapse = GPhoto2Timelapse(seq, logr)

    # and we're off!
    lapse.take_next_picture()

    save_state_to_disk('results.json')

except OSError as e:
    logr.log("no {} file found in root directory (error: {})".format(args.file, e))

except ValueError:
    logr.log("malformed json found in root directory.  please ensure minimal format of [{ \"name\": \"\", \"ts\": 1474075839955 }")

except TimelapseError as e:
    logr.log("> Timelapse aborted, rebooting system.")
    save_state_to_disk('saved_state.json')

except Exception as e:
    logr.log("> Unknown error occurred, rebooting system (error: {})".format(e))
    save_state_to_disk('saved_state.json')
