"""
Main client for the Eesee account.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, List
from signalrcore.hub_connection_builder import HubConnectionBuilder

import aiohttp

from .charger import Charger
from .exceptions import (
    AuthorizationFailedException,
    NotFoundException,
    ServerFailureException,
    TooManyRequestsException,
)
from .site import Site, SiteState
from .utils import convert_stream_data

__VERSION__ = "0.7.31"

_LOGGER = logging.getLogger(__name__)

SR_RECONNECT_TIMEOUT = 60


async def raise_for_status(response):
    if 400 <= response.status:
        e = aiohttp.ClientResponseError(
            response.request_info,
            response.history,
            code=response.status,
            headers=response.headers,
        )

        if "json" in response.headers.get("CONTENT-TYPE", ""):
            data = await response.json()
            e.message = str(data)
        else:
            data = await response.text()

        if 400 == response.status:
            _LOGGER.error("Bad request service " + f"({response.status}: {data} {response.url})")
            raise AuthorizationFailedException(data)
        elif 401 == response.status:
            _LOGGER.debug("Unautorized " + f"({response.status}: {data} {response.url})")
            raise AuthorizationFailedException(data)
        elif 403 == response.status:
            _LOGGER.error("Forbidden service " + f"({response.status}: {data} {response.url})")
        elif 404 == response.status:
            # Getting this error when getting or deleting charge schedules which doesn't exist (empty)
            _LOGGER.debug("Not found " + f"({response.status}: {data} {response.url})")
            raise NotFoundException(data)
        elif 429 == response.status:
            _LOGGER.debug("Too many requests " + f"({response.status}: {data} {response.url})")
            raise TooManyRequestsException(data)
        elif response.status > 500:
            _LOGGER.warning("Server failure" + f"({response.status}: {response.url})")
            raise ServerFailureException(data)
        else:
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
        self.sr_base = "https://api.easee.cloud/hubs/chargers"
        self.token = {}
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json;charset=UTF-8",
        }
        if session is None:
            self.session = aiohttp.ClientSession()
        else:
            self.session = session

        self.sr_subscriptions = {}
        self.sr_connection = None
        self.sr_connected = False
        self.sr_connect_in_progress = False
        self.running_loop = None
        self.event_loop = None

    async def post(self, url, **kwargs):
        _LOGGER.debug("POST: %s (%s)", url, kwargs)
        await self._verify_updated_token()
        response = await self.session.post(f"{self.base}{url}", headers=self.headers, **kwargs)
        await self.check_status(response)
        return response

    async def put(self, url, **kwargs):
        _LOGGER.debug("PUT: %s (%s)", url, kwargs)
        await self._verify_updated_token()
        response = await self.session.put(f"{self.base}{url}", headers=self.headers, **kwargs)
        await self.check_status(response)
        return response

    async def get(self, url, **kwargs):
        _LOGGER.debug("GET: %s (%s)", url, kwargs)
        await self._verify_updated_token()
        response = await self.session.get(f"{self.base}{url}", headers=self.headers, **kwargs)
        await self.check_status(response)
        return response

    async def delete(self, url, **kwargs):
        _LOGGER.debug("DELETE: %s (%s)", url, kwargs)
        await self._verify_updated_token()
        response = await self.session.delete(f"{self.base}{url}", headers=self.headers, **kwargs)
        await self.check_status(response)
        return response

    # TODO: Quick fix for the auth fail errors due to something wrong with refresh token logic
    async def check_status(self, response):
        try:
            await raise_for_status(response)
        except AuthorizationFailedException:
            _LOGGER.debug("Re authorizing due to 401")
            await self.connect()
            # rethrow it
            await raise_for_status(response)
        except Exception as ex:
            _LOGGER.debug("Got other exception from status: %s", type(ex).__name__)
            raise

    async def _verify_updated_token(self):
        """
        Make sure there is a valid token
        """
        if "accessToken" not in self.token:
            await self.connect()
        accessToken = self.token["accessToken"]
        self.headers["Authorization"] = f"Bearer {accessToken}"
        _LOGGER.debug(
            "verify_updated_token: %s, %s, %s",
            self.token["expires"],
            datetime.now(),
            self.token["expires"] < datetime.now(),
        )
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
        _LOGGER.debug("getting token for user: %s", self.username)
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
        try:
            res = await self.session.post("/api/accounts/refresh_token", json=data)
            await self._handle_token_response(res)
        except AuthorizationFailedException:
            _LOGGER.debug("Could not get new access token from refresh token, getting new one")
            await self.connect()

    async def close(self):
        """
        Close the underlying aiohttp session
        """
        if self.session and self.external_session is False:
            await self.session.close()
            self.session = None

        await self._sr_disconnect()

    def _sr_token(self):
        """
        Return access token to signalr library, called from signalr thread, internal use only
        """
        if self.running_loop is not None:
            future = asyncio.run_coroutine_threadsafe(self._verify_updated_token(), self.event_loop)
            future.result()
        if "accessToken" not in self.token:
            accessToken = ""
        else:
            accessToken = self.token["accessToken"]
        return accessToken

    def _sr_open_cb(self):
        """
        Signalr connected callback - called from signalr thread, internal use only
        """
        _LOGGER.debug("SignalR stream connected")
        for id in self.sr_subscriptions:
            _LOGGER.debug("Subscribing to %s", id)
            self.sr_connection.send("SubscribeWithCurrentState", [id, True])
        self.sr_connected = True

    def _sr_close_cb(self):
        """
        Signalr disconnected callback - called from signalr thread, internal use only
        """
        _LOGGER.debug("SignalR stream disconnected")
        self.sr_connected = False

    def _sr_product_update_cb(self, stuff: list):
        """
        Signalr new data recieved callback - called from signalr thread, internal use only
        """
        if self.running_loop is not None:
            for data in stuff:
                asyncio.run_coroutine_threadsafe(self._sr_callback(data), self.event_loop)

    def _sr_charger_update_cb(self, stuff: list):
        """
        Signalr new data recieved callback - called from signalr thread, internal use only
        """
        if self.running_loop is not None:
            for data in stuff:
                asyncio.run_coroutine_threadsafe(self._sr_callback(data), self.event_loop)

    async def _sr_callback(self, stuff: list):
        """
        Signalr callback handler - internal use only
        """
        if stuff["mid"] in self.sr_subscriptions:
            callback = self.sr_subscriptions[stuff["mid"]]
            value = convert_stream_data(stuff["dataType"], stuff["value"])
            await callback(stuff["mid"], stuff["dataType"], stuff["id"], value)
        else:
            _LOGGER.debug("No callback found for %s", stuff["mid"])

    async def _sr_connect(self):
        """
        Signalr connect - internal use only
        """
        self.running_loop = asyncio.get_running_loop()
        self.event_loop = asyncio.get_event_loop()

        if self.sr_connect_in_progress is False:
            self.sr_connect_in_progress = True
            asyncio.ensure_future(self._sr_connect_loop())

    async def _sr_connect_loop(self):
        """
        Signalr connect loop - internal use only
        """
        if self.sr_connection is not None:
            return

        _LOGGER.debug("SR connect loop")

        options = {"access_token_factory": self._sr_token}
        self.sr_connection = (
            HubConnectionBuilder()
            .with_url(self.sr_base, options)
            .configure_logging(logging.CRITICAL)
            .with_automatic_reconnect(
                {"type": "raw", "keep_alive_interval": 20, "reconnect_interval": SR_RECONNECT_TIMEOUT}
            )
            .build()
        )
        self.sr_connection.on_open(lambda: self._sr_open_cb())
        self.sr_connection.on_close(lambda: self._sr_close_cb())
        self.sr_connection.on("ProductUpdate", self._sr_product_update_cb)
        # The ChargerUpdate callback seems redundant?
        # self.sr_connection.on("ChargerUpdate", self._sr_charger_update_cb)

        await self._verify_updated_token()
        while True:
            """ The signalrcore lib start function does blocking I/O, so can not be called directly """
            try:
                await self.running_loop.run_in_executor(None, self.sr_connection.start)
            except Exception as ex:
                _LOGGER.debug("SR start exception: %s. Retry in %d seconds", type(ex).__name__, SR_RECONNECT_TIMEOUT)
                await asyncio.sleep(SR_RECONNECT_TIMEOUT)
                continue

            break

        self.sr_connect_in_progress = False

    def sr_is_connected(self):
        return self.sr_connected

    async def sr_subscribe(self, product, callback):
        """
        Subscribe to signalr events for product, callback will be called as async callback(product_id, data_type, data_id, value)
        """
        if product.id in self.sr_subscriptions:
            return

        _LOGGER.debug("Subscribing to %s", product.id)
        self.sr_subscriptions[product.id] = callback
        if self.sr_connected is True:
            self.sr_connection.send("SubscribeWithCurrentState", [product.id, True])
        else:
            await self._sr_connect()

    async def sr_unsubscribe(self, product):
        """
        Unsubscribe from signalr events for product
        BUG: Does not work
        """
        _LOGGER.debug("Unsubscribing from %s", product.id)
        if product.id in self.sr_subscriptions:
            del self.sr_subscriptions[product.id]
            await self._sr_disconnect()
            await self._sr_connect()

    async def _sr_disconnect(self):
        """
        Disconnect the signalr stream - internal use only
        """
        if self.sr_connection is not None:
            self.sr_connection.stop()
            self.sr_connection = None

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

    async def get_site_state(self, id: str) -> SiteState:
        """ Get site state """
        state = await (await self.get(f"/api/sites/{id}/state")).json()
        return SiteState(state)

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
