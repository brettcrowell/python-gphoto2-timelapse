import time
from datetime import datetime

class Logger:

    messages = []

    def __init__(self, restored_log = None):

        if(restored_log):
            # if we are restoring from saved state, we'll need to include the old log
            self.messages = restored_log

    def get_log(self):
        return self.messages

    def log(self, message):
        current_ts = int(round(time.time() * 1000))
        self.messages.append({
            "ts": current_ts,
            "message": message
        })
        print(message)