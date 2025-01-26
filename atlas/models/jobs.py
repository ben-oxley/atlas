from enum import Enum

# class syntax
class JobType(Enum):
    DOWNLOAD = 1
    TILE = 2
    DETECT = 3

class JobStatus(Enum):
    NOT_STARTED = 1
    RUNNING = 2
    COMPLETE = 3
    ERROR = 4
    TIMEOUT = 5