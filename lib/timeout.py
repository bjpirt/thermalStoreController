import time
from typing import Union


class Timeout:
    # pylint: disable=E1101,E1136
    def __init__(self, interval: Union[float, None] = None) -> None:
        self.__ready_time: int = -1
        self.__last_interval: float
        if interval is not None:
            self.__last_interval = interval

    def set(self, interval: float) -> None:
        self.__ready_time = time.ticks_add(  # type: ignore
            time.ticks_ms(), int(interval * 1000))  # type: ignore
        self.__last_interval = interval

    def reset(self) -> None:
        self.set(self.__last_interval)

    @property
    def ready(self) -> bool:
        return time.ticks_diff(self.__ready_time, time.ticks_ms()) <= 0  # type: ignore
