import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set, Union, cast
from enum import Enum

from aiohttp.helpers import NO_EXTENSIONS
from .charger import Charger
from .site import Circuit, Site


__VERSION__ = "0.7.6"

_LOGGER = logging.getLogger(__name__)


async def raise_for_status(response):
    if 400 <= response.status:
        e = aiohttp.ClientResponseError(
            response.request_info, response.history, code=response.status, headers=response.headers,
        )

        if "json" in response.headers.get("CONTENT-TYPE", ""):
            data = await response.json()
            e.message = str(data)
        else:
            data = await response.text()

        if 400 == response.status:
            _LOGGER.error(
                "Bad request service " + f"({response.status}: {data} {response.url})"
            )
        elif 403 == response.status:
            _LOGGER.error(
                "Forbidden service " + f"({response.status}: {data} {response.url})"
            )
        elif 404 == response.status:
            _LOGGER.error(
                "Service not found " + f"({response.status}: {data} {response.url})"
            )
        else:
            # raise Exception(data) from e
            _LOGGER.error("Error in request to Easee API: %s", data)
            raise Exception(data) from e
        return False
    else:
        return True


class Easee:
    def __init__(self, username, password, session: aiohttp.ClientSession = None):
        self.username = username
        self.password = password
        _LOGGER.info("Easee python library version: %s", __VERSION__)

        _LOGGER.debug("user: '%s', pass: '%s'", username, password)
        self.base = "https://api.easee.cloud"
        self.token = {}
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json;charset=UTF-8",
        }
        self.sites = [Site]
        self.circuits = [Circuit]
        self.chargers = [Charger]

        if session is None:
            self.session = aiohttp.ClientSession()
        else:
            self.session = session

    async def post(self, url, **kwargs):
        _LOGGER.debug("post: %s (%s)", url, kwargs)
        await self._verify_updated_token()
        response = await self.session.post(f"{self.base}{url}", headers=self.headers, **kwargs)
        await raise_for_status(response)
        return response

    async def get(self, url, **kwargs):
        _LOGGER.debug("get: %s (%s)", url, kwargs)
        await self._verify_updated_token()
        response = await self.session.get(f"{self.base}{url}", headers=self.headers, **kwargs)
        await raise_for_status(response)
        return response

    async def _verify_updated_token(self):
        """
        Make sure there is a valid token
        """
        if "accessToken" not in self.token:
            await self.connect()
        accessToken = self.token["accessToken"]
        self.headers["Authorization"] = f"Bearer {accessToken}"
        if self.token["expires"] < datetime.now():
            self._refresh_token()

    async def _handle_token_response(self, res):
        """
        Handle the token request and set new datetime when it expires
        """
        self.token = await res.json()
        _LOGGER.debug("TOKEN: %s", self.token)
        expiresIn = int(self.token["expiresIn"])
        now = datetime.now()
        self.token["expires"] = now + timedelta(0, expiresIn)

    async def connect(self):
        """
        Gets initial token
        """
        data = {"userName": self.username, "password": self.password}
        _LOGGER.debug("getting token with creds: %s", data)
        response = await self.session.post(f"{self.base}/api/accounts/token", json=data)
        await raise_for_status(response)
        await self._handle_token_response(response)

    async def _refresh_token(self):
        """
        Refresh token
        """
        data = {
            "accessToken": self.token["accessToken"],
            "refreshToken": self.token["refreshToken"],
        }
        _LOGGER.debug("Refreshing access token")
        res = await self.post("/api/accounts/refresh_token", json=data)
        await self._handle_token_response(res)

    async def close(self):
        """
        Close the underlying aiohttp session
        """
        if self.session:
            await self.session.close()
            self.session = None

    def get_chargers(self) -> List[Charger]:
        return self.chargers

    async def get_site(self, id: int) -> Site:
        """ get site by id """
        data = await (await self.get(f"/api/sites/{id}")).json()
        _LOGGER.debug("Site:  %s", data)
        return Site(data, self)

    def get_sites(self) -> List[Site]:
        return self.sites

    def get_circuits(self) -> List[Circuit]:
        return self.circuits

    async def get_active_countries(self) -> List[Any]:
        records = await (await self.get("/api/resources/countries/active")).json()
        _LOGGER.debug("Active countries:  %s", records)
        return records

    async def get_currencies(self) -> List[Any]:
        records = await (await self.get("/api/resources/currencies")).json()
        _LOGGER.debug("Currencies:  %s", records)
        return records

    async def async_update(self):
        self.populate()

    async def populate(self):
        """ Get all sites for logged in account and populate circuits and chargers """
        self.sites.clear()
        self.circuits.clear()
        self.chargers.clear()

        records = await (await self.get("/api/sites")).json()
        _LOGGER.debug("Sites:  %s", records)
        self.sites = await asyncio.gather(*[self.get_site(r["id"]) for r in records])
        for site in self.sites:
            for circuit in site.get_circuits():
                self.circuits.append(circuit)
                for charger in circuit.get_chargers():
                    self.chargers.append(charger)
        return self.sites