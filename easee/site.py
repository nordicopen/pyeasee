import logging
from typing import Any, Dict, List

from .utils import BaseDict, validate_iso8601
from .charger import Charger

_LOGGER = logging.getLogger(__name__)


class Circuit(BaseDict):
    def __init__(self, data: Dict[str, Any], site: Any, easee: Any):
        super().__init__(data)
        self.id: int = data["id"]
        self.name: str = data["panelName"]
        self.easee = easee
        self.site = site
        self.chargers: List[Charger] = [Charger(c, self, self.easee) for c in data["chargers"]]

    def get_name(self):
        return self.name

    def get_chargers(self):
        return self.chargers

    async def set_circuit_maxcurrent(self, maxCircuitCurrent):
        """ Set circuit max current settings and post to Easee cloud """
        json = {
                "maxCircuitCurrentP1": maxCircuitCurrent,
                "maxCircuitCurrentP2": maxCircuitCurrent,
                "maxCircuitCurrentP3": maxCircuitCurrent,
                }
        return await self.easee.post(f"/api/sites/{self.site.id}/circuits/{self.id}/settings", json=json)

    async def set_circuit_dynamicCurrent(self, dynamicCircuitCurrent):
        """ Set circuit dynamic current settings and post to Easee cloud """
        json = {
                "dynamicCircuitCurrentP1": dynamicCircuitCurrent,
                "dynamicCircuitCurrentP2": dynamicCircuitCurrent,
                "dynamicCircuitCurrentP3": dynamicCircuitCurrent,
                }
        return await self.easee.post(f"/api/sites/{self.site.id}/circuits/{self.id}/settings", json=json)

    async def set_rated_current(self, ratedCurrentFuseValue):
        """ Set rated current and post to Easee cloud """
        json = {
                "ratedCurrentFuseValue": ratedCurrentFuseValue
                }
        return await self.easee.post(f"/api/sites/{self.site.id}/circuits/{self.id}/rated_current", json=json)


class Site(BaseDict):
    def __init__(self, data: Dict[str, Any], easee: Any):
        super().__init__(data)
        self.id: int = data["id"]
        self.name: str = data["name"]
        self.easee = easee
        self.circuits: List[Circuit] = [Circuit(c, self, self.easee) for c in data["circuits"]]

    def get_circuits(self): 
        return self.circuits

    def get_number_of_chargers(self):
        circuits = self.get_circuits()
        number_of_chargers = 0
        for c in circuits:
            number_of_chargers += len(c["chargers"])
        return number_of_chargers
