try:
    import RPi.GPIO as _GPIO
    _available = True
except ImportError:
    _GPIO = None
    _available = False


class PowerRelay:
    def __init__(self, state):
        self.pin = state["preferences"]["power_signal_pin"]
        self._setup()

    def _setup(self):
        if _available:
            _GPIO.setmode(_GPIO.BCM)
            _GPIO.setup(self.pin, _GPIO.OUT)
            _GPIO.output(self.pin, _GPIO.LOW)

    def on(self):
        if _available:
            _GPIO.output(self.pin, _GPIO.LOW)

    def off(self):
        if _available:
            _GPIO.output(self.pin, _GPIO.HIGH)

    @staticmethod
    def is_available():
        return _available
