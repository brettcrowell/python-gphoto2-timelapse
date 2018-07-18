#!/usr/bin/env python3

import json
from timelapse import GPhoto2Timelapse
from sequence import Sequence
from logger import Logger
from timelapse_errors import TimelapseError
from uploader import S3BucketUploader
from argparse import ArgumentParser, FileType
import time
import os

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
            uploader = S3BucketUploader()

            lapse = GPhoto2Timelapse(seq, uploader, logr, restored_state["lapse"])

            logr.log("State restored from disk.  Here we go again!")

    except (OSError, ValueError):

        parser = ArgumentParser()

        parser.add_argument(
            '-s',
            '--span',
            help='The number of hours your timelapse will run for, starting now.',
            default=24,
            type=int
        )

        parser.add_argument(
            '-d',
            '--duration',
            help='The duration of the assembled timelapse, in seconds.',
            default=60,
            type=int
        )

        parser.add_argument(
            '-f',
            '--fps',
            help='The frame rate, in frames per second, of the assembled timelapse.',
            default=30,
            type=int
        )

        parser.add_argument(
            '-n',
            '--name',
            help='The name of the timelapse.  Also serves as the directory name for frames.',
            default="timelapse",
        )

        parser.add_argument(
            '-b',
            '--bucket',
            help='The name of the S3 Bucket where frames will be uploaded.',
            default="bc-timelapse"
        )

        parser.add_argument(
            '-i',
            '--input',
            help='The relative path of a JSON file containing an array of timestamps.  Overrides --span, --duration, and --fps',
            default=None,
            type=FileType("r")
        )

        args = parser.parse_args()

        if args.input:

            with args.input as data_file:

                # otherwise start a new one
                exposures = json.load(data_file)

        else:

            epoch = int(round(5000 + (time.time() * 1000)))

            # calculate the interval between captures and the total #/frames
            numFrames = args.duration * args.fps
            intervalMilliseconds = round(
                (args.span * 60 * 60 * 1000) / numFrames)

            exposures = list(map(
                (lambda i: dict([
                    ("name", args.name),
                    ("ts", epoch + (i * intervalMilliseconds))
                ])),
                range(numFrames)
            ))

        # make sure these are globals
        logr = Logger()
        seq = Sequence(exposures, logr)
        uploader = S3BucketUploader()

        lapse = GPhoto2Timelapse(seq, uploader, logr)

        logr.log("New lapse started by `timelapse_server`")

    # and we're off!
    lapse.take_next_picture()

    save_state_to_disk('results.json')

except OSError as e:
    logr.log("no data.json file found in root directory (error: {})".format(e))

except ValueError:
    logr.log("malformed json found in root directory.  please ensure minimal format of [{ \"name\": \"\", \"ts\": 1474075839955 }")

except TimelapseError as e:
    logr.log("> Timelapse aborted, rebooting system.")
    save_state_to_disk('saved_state.json')

except Exception as e:
    logr.log("> Unknown error occurred, rebooting system (error: {})".format(e))
    save_state_to_disk('saved_state.json')
