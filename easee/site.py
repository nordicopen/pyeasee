import logging
from typing import Any, Dict, List
from .utils import BaseDict, validate_iso8601
from .charger import Charger

_LOGGER = logging.getLogger(__name__)


class Circuit(BaseDict):
    def __init__(self, entries: Dict[str, Any], easee: Any):
        super().__init__(entries)
        self.easee = easee

    def get_chargers(self) -> List[Charger]:
        return [Charger(c["id"], c["name"], self.easee) for c in self["chargers"]]


class Site(BaseDict):
    def __init__(self, data: Dict[str, Any], easee: Any):
        super().__init__(data)
        self.easee = easee

    def get_circuits(self) -> List[Circuit]:
        return [Circuit(c, self.easee) for c in self["circuits"]]


"""
{
  "contactInfo": {
    "installerName": "string",
    "installerPhoneNumber": "string",
    "ownerName": "string",
    "ownerPhoneNumber": "string",
    "company": "string"
  },
  "costPerKWh": 0,
  "vat": 0,
  "costPerKwhExcludeVat": 0,
  "currencyId": "string",
  "partnerId": 0,
  "siteType": 1,
  "ratedCurrent": 0,
  "useDynamicMaster": true,
  "circuits": [
    {
      "id": 0,
      "siteId": 0,
      "circuitPanelId": 0,
      "panelName": "string",
      "ratedCurrent": 0,
      "chargers": [
        {
          "id": "string",
          "name": "string",
          "color": 1,
          "createdOn": "2020-07-14T11:51:21.965Z",
          "updatedOn": "2020-07-14T11:51:21.965Z",
          "backPlate": {
            "id": "string",
            "masterBackPlateId": "string"
          },
          "levelOfAccess": 1,
          "productCode": 1
        }
      ],
      "masterBackplate": {
        "id": "string",
        "masterBackPlateId": "string"
      },
      "useDynamicMaster": true
    }
  ],
  "equalizers": [
    {
      "id": "string",
      "name": "string",
      "siteId": 0,
      "circuitId": 0
    }
  ],
  "createdOn": "2020-07-14T11:51:21.965Z",
  "updatedOn": "2020-07-14T11:51:21.965Z",
  "id": 0,
  "siteKey": "string",
  "name": "string",
  "levelOfAccess": 1,
  "address": {
    "street": "string",
    "buildingNumber": "string",
    "zip": "string",
    "area": "string",
    "country": {
      "id": "string",
      "name": "string",
      "phonePrefix": 0
    },
    "latitude": 0,
    "longitude": 0,
    "altitude": 0
  }
}
"""
