import logging
from typing import Any, Dict, List

from .utils import BaseDict
from .charger import Charger, ChargerConfig, ChargerState

_LOGGER = logging.getLogger(__name__)


class Equalizer(BaseDict):
    def __init__(self, data: Dict[str, Any], site: Any, easee: Any):
        super().__init__(data)
        self.id: int = data["id"]
        self.site = site
        self.easee = easee

    async def get_state(self):
        """ Get Equalizer state """
        return await (await self.easee.get(f"/api/equalizers/{self.id}/state")).json()


class Circuit(BaseDict):
    """ Represents a Circuit """

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


class SiteState(BaseDict):
    """ Represents the site state as received through /sites/<id>/state """

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)

    def get_charger_config(self, charger_id: str) -> ChargerConfig:
        """ get config for charger from the instance data"""
        for circuit in self["circuitStates"]:
            for charger_data in circuit["chargerStates"]:
                if charger_data["chargerID"] == charger_id:
                    return ChargerConfig(charger_data["chargerConfig"])

        return None

    def get_charger_state(self, charger_id: str) -> ChargerState:
        """ get state for charger from the instance data"""
        for circuit in self["circuitStates"]:
            for charger_data in circuit["chargerStates"]:
                if charger_data["chargerID"] == charger_id:
                    return ChargerState(charger_data["chargerState"])

        return None


class Site(BaseDict):
    """ Represents a Site """

    def __init__(self, data: Dict[str, Any], easee: Any):
        super().__init__(data)
        self.id: int = data["id"]
        self.easee = easee

    def get_circuits(self) -> List[Circuit]:
        """ Get circuits for the site """
        return [Circuit(c, self, self.easee) for c in self["circuits"]]

    def get_equalizers(self) -> List[Equalizer]:
        """ Get equalizers for the site """
        return [Equalizer(e, self, self.easee) for e in self["equalizers"]]

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

        json = {"costPerKWh": costPerKWh}

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
