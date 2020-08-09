import logging
from typing import Any, Dict, List

from .utils import BaseDict
from .charger import Charger

_LOGGER = logging.getLogger(__name__)


class Circuit(BaseDict):
    def __init__(self, data: Dict[str, Any], site: Any, easee: Any):
        super().__init__(data)
        self.id: int = data["id"]
        self.site = site
        self.easee = easee

    async def set_dynamic_current(self, currentP1: int, currentP2: int = None, currentP3: int = None):
        """ Set circuit dynamic current """
        json = {
            "dynamicCircuitCurrentP1": currentP1,
            "dynamicCircuitCurrentP2": currentP2 if currentP2 is not None else currentP1,
            "dynamicCircuitCurrentP3": currentP3 if currentP3 is not None else currentP1,
        }
        return await self.easee.post(f"/api/sites/{self.site.id}/circuits/{self.id}/settings", json=json)

    async def set_max_current(self, currentP1: int, currentP2: int = None, currentP3: int = None):
        """ Set circuit max current """
        json = {
            "maxCircuitCurrentP1": currentP1,
            "maxCircuitCurrentP2": currentP2 if currentP2 is not None else currentP1,
            "maxCircuitCurrentP3": currentP3 if currentP3 is not None else currentP1,
        }
        return await self.easee.post(f"/api/sites/{self.site.id}/circuits/{self.id}/settings", json=json)

    async def set_rated_current(self, ratedCurrentFuseValue: int):
        """ Set circuit rated current - requires elevated access (installers only) """
        json = {"ratedCurrentFuseValue": ratedCurrentFuseValue}
        return await self.easee.post(f"/api/sites/{self.site.id}/circuits/{self.id}/rated_current", json=json)

    def get_chargers(self) -> List[Charger]:
        return [Charger(c, self.easee, self.site, self) for c in self["chargers"]]


class Site(BaseDict):
    def __init__(self, data: Dict[str, Any], easee: Any):
        super().__init__(data)
        self.id: int = data["id"]
        self.easee = easee

    def get_circuits(self) -> List[Circuit]:
        return [Circuit(c, self, self.easee) for c in self["circuits"]]

    async def set_name(self, name: str):
        """ Set name for the site """
        json = {**self.get_data(), "name": name}
        return await self.easee.put(f"/api/sites/{self.id}", json=json)

    async def set_currency(self, currency: str):
        """ Set currency for the site """
        json = {**self.get_data(), "currencyId": currency}
        return await self.easee.put(f"/api/sites/{self.id}", json=json)

    async def set_price(
        self, costPerKWh: float, vat: float = None, currency: str = None, costPerKwhExcludeVat: float = None,
    ):
        """ Set price per kWh for the site """

        json = {
            "costPerKWh": costPerKWh,
        }

        if vat is None:
            vat = self.get("vat")

        if currency is None:
            currency = self.get("currencyId")

        if costPerKwhExcludeVat is None:
            costPerKwhExcludeVat = costPerKWh / (100.0 + vat) * 100.0

        json = {
            "currencyId": currency,
            "costPerKWh": costPerKWh,
            "vat": vat,
            "costPerKwhExcludeVat": costPerKwhExcludeVat,
        }

        return await self.easee.post(f"/api/sites/{self.id}/price", json=json)
