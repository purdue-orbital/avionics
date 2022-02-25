from __future__ import annotations

import json
from typing import Any, Dict, List
import traceback

from orbitalcoms import ComsMessage, create_serial_launch_station

# from Radio import Radio
class Comm:
    __instance: _CommSingleton | None = None

    def __init__(self) -> None:
        raise RuntimeError("Constructor should not be called")

    @classmethod
    def get_instance(cls, port: str, baudrate: int) -> _CommSingleton:
        if cls.__instance is None:
            cls.__instance = _CommSingleton(port, baudrate)
        return cls.__instance


class _CommSingleton:
    def __init__(self, port: str = "/dev/ttyuUSB0", baudrate: int = 9600) -> None:
        try:
            self.__radio = create_serial_launch_station(port, baudrate)
        except Exception:
            traceback.print_exc()

    def send(self, command: Dict[Any, Any]) -> None:
        print(f"Sending: {command}")
        if not self.__radio.send(json.dumps(command)):
            print("Message failed to send")

    def bind(self, queue: List[ComsMessage]) -> None:
        self.__radio.bind_queue(queue)

    def getLaunchFlag(self) -> bool:
        return self.__radio.getLaunchFlag()

    def getQDMFlag(self) -> bool:
        return self.__radio.getQDMFlag()

    def getAbortFlag(self) -> bool:
        return self.__radio.getAbortFlag()

    def getStabFlag(self) -> bool:
        return self.__radio.getStabFlag()

    def getArmedFlag(self) -> bool:
        self.__radio.getArmedFlag()
