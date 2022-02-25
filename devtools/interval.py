from threading import Thread, Event
from typing import Any, Callable


class IntervalThread(Thread):
    """
    Spawn a Thread to repeat at a given interval
    Arguments:
        obj : a Function object to be executed
    """

    def __init__(self, function: Callable[[], Any], freq: float):
        super().__init__(daemon=True)
        self.stop_event = Event()
        self.fn = function
        self.freq = freq

    def run(self):
        while not self.stop_event.wait(1 / self.freq):
            self.fn()

    def stop(self):
        self.stop_event.set()
