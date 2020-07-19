import logging
from typing import Any, Dict, List

from .utils import BaseDict, validate_iso8601
from .charger import Charger

_LOGGER = logging.getLogger(__name__)


class Circuit(BaseDict):
    def __init__(self, data: Dict[str, Any], easee: Any):
        super().__init__(data)
        self.id: int = data["id"]
        self.easee = easee

    def get_chargers(self) -> List[Charger]:
        return [Charger(c, self.easee) for c in self["chargers"]]


class Site(BaseDict):
    def __init__(self, data: Dict[str, Any], easee: Any):
        super().__init__(data)
        self.id: int = data["id"]
        self.easee = easee

    def get_circuits(self) -> List[Circuit]:
        return [Circuit(c, self.easee) for c in self["circuits"]]
