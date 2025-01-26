
from typing import List
from attr import dataclass
from datetime import datetime


@dataclass
class Tile:
    x:int
    y:int
    z:int

@dataclass
class TileMetricDatapoint:
    time:datetime
    count:int

@dataclass 
class TileMetricTimeline:
    values:List[TileMetricDatapoint]