#!/usr/bin/env python3

import argparse
import json
import os
import re

from timelapse import GPhoto2Timelapse
from sequence import Sequence, DelaySequence
from logger import Logger
from timelapse_errors import TimelapseError

def parse_duration(value):
    """Parse a duration string like '2h', '30m', '90s', or '90' into seconds."""
    match = re.fullmatch(r'(\d+(?:\.\d+)?)\s*([hms])?', value.strip())
    if not match:
        raise argparse.ArgumentTypeError("invalid duration '{}' (expected e.g. 2h, 30m, 90s, or 90)".format(value))
    amount = float(match.group(1))
    unit = match.group(2)
    if unit == 'h':
        return amount * 3600
    elif unit == 'm':
        return amount * 60
    else:
        return amount

parser = argparse.ArgumentParser(description="Run a clock-time based timelapse")
parser.add_argument("--file", help="JSON file containing exposure sequence")
parser.add_argument("--delay", type=int, help="Fixed delay in seconds between exposures (runs indefinitely)")
parser.add_argument("--duration", type=str, help="Real-time capture duration (e.g. 2h, 30m, 90s)")
parser.add_argument("--output", type=str, help="Desired output video length (e.g. 1m, 30s)")
parser.add_argument("--fps", type=int, default=30, help="Output video frame rate (default: 30)")
args = parser.parse_args()

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
        elif args.delay:
            # run indefinitely with fixed delay between exposures
            seq = DelaySequence(args.delay, logr)
            logr.log("New lapse started with {}s delay (runs indefinitely)".format(args.delay))
        else:
            # compute delay from duration/output/fps
            duration_s = parse_duration(args.duration or "24h")
            output_s = parse_duration(args.output or "1m")
            total_frames = int(output_s * args.fps)
            delay = duration_s / total_frames

            # only cap frames if the user explicitly set --duration or --output
            max_images = total_frames if (args.duration or args.output) else None
            seq = DelaySequence(delay, logr, max_images=max_images)

            if max_images:
                logr.log("New lapse started with {:.1f}s delay ({} frames)".format(delay, max_images))
            else:
                logr.log("New lapse started with {:.1f}s delay (runs indefinitely)".format(delay))

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
