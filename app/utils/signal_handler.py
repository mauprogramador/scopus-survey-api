from asyncio import Event as AsyncEvent
from signal import SIGINT, SIGTERM, signal
from threading import Event as ThreadEvent


class SignalHandler:
    """Set signal handlers to set the shutdown event flag"""

    def __init__(self, for_async: bool = None):
        """Set signal handlers to set the shutdown event flag"""
        self.event = ThreadEvent() if for_async is None else AsyncEvent()

        signal(SIGINT, self.__shutdown)
        signal(SIGTERM, self.__shutdown)

    def __shutdown(self, *_) -> None:
        self.event.set()
