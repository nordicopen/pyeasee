"""
Main client for the Eesee account.
"""
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Any, List
from .charger import Charger
from .site import Site


__VERSION__ = "0.7.10"

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
            _LOGGER.error("Bad request service " + f"({response.status}: {data} {response.url})")
        elif 403 == response.status:
            _LOGGER.error("Forbidden service " + f"({response.status}: {data} {response.url})")
        elif 404 == response.status:
            _LOGGER.error("Service not found " + f"({response.status}: {data} {response.url})")
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
        self.external_session = True if session else False

        _LOGGER.info("Easee python library version: %s", __VERSION__)

        self.base = "https://api.easee.cloud"
        self.token = {}
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json;charset=UTF-8",
        }
        if session is None:
            self.session = aiohttp.ClientSession()
        else:
            self.session = session

    async def post(self, url, **kwargs):
        _LOGGER.debug("POST: %s (%s)", url, kwargs)
        await self._verify_updated_token()
        response = await self.session.post(f"{self.base}{url}", headers=self.headers, **kwargs)
        await raise_for_status(response)
        return response

    async def put(self, url, **kwargs):
        _LOGGER.debug("PUT: %s (%s)", url, kwargs)
        await self._verify_updated_token()
        response = await self.session.put(f"{self.base}{url}", headers=self.headers, **kwargs,)
        await raise_for_status(response)
        return response

    async def get(self, url, **kwargs):
        _LOGGER.debug("GET: %s (%s)", url, kwargs)
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
        Connect and gets initial token
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
        if self.session and self.external_session is False:
            await self.session.close()
            self.session = None

    async def get_chargers(self) -> List[Charger]:
        """
        Retrieve all chargers
        """
        records = await (await self.get("/api/chargers")).json()
        _LOGGER.debug("Chargers:  %s", records)
        return [Charger(k, self) for k in records]

    async def get_site(self, id: int) -> Site:
        """ get site by id """
        data = await (await self.get(f"/api/sites/{id}?detailed=true")).json()
        _LOGGER.debug("Site:  %s", data)
        return Site(data, self)

    async def get_sites(self) -> List[Site]:
        """ Get all sites """
        records = await (await self.get("/api/sites")).json()
        _LOGGER.debug("Sites:  %s", records)
        sites = await asyncio.gather(*[self.get_site(r["id"]) for r in records])
        return sites

    async def get_active_countries(self) -> List[Any]:
        """ Get all active countries """
        records = await (await self.get("/api/resources/countries/active")).json()
        _LOGGER.debug("Active countries:  %s", records)
        return records

    async def get_currencies(self) -> List[Any]:
        """ Get all currencies """
        records = await (await self.get("/api/resources/currencies")).json()
        _LOGGER.debug("Currencies:  %s", records)
        return records
