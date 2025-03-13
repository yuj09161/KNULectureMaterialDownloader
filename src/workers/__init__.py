from enum import Enum, auto
from typing import NamedTuple


class MaterialTypes(Enum):
    DOCUMENT = auto()
    VIDEO = auto()

class LectureMaterial(NamedTuple):
    name: str
    type_: MaterialTypes
    url: str
