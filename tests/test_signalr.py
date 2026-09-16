import aiohttp
from aioresponses import aioresponses
from pysignalr.client import SignalRClient
import pytest
import pytest_asyncio

from pyeasee import Easee


@pytest_asyncio.fixture
async def aioresponse():
    with aioresponses() as m:
        yield m


@pytest_asyncio.fixture
async def aiosession():
    return aiohttp.ClientSession()


@pytest.mark.asyncio
async def test_negotiate_forwards_cookies_to_ws_headers(aiosession, aioresponse):
    """Set-Cookie on the negotiate response
    must be forwarded as a Cookie header on the WebSocket handshake."""
    easee = Easee("+46070123456", "password", aiosession)

    aioresponse.post(
        f"{easee.sr_base}/negotiate",
        payload={"connectionId": "abc-123"},
        headers={"Set-Cookie": "AWSALB=sticky-value"},
    )

    client = SignalRClient(easee.sr_base, headers=easee.sr_headers)
    await client._transport._negotiate()

    assert client._transport._headers["Cookie"] == "AWSALB=sticky-value"

    await easee.close()
    await aiosession.close()


@pytest.mark.asyncio
async def test_negotiate_without_cookies_leaves_headers_untouched(aiosession, aioresponse):
    easee = Easee("+46070123456", "password", aiosession)

    aioresponse.post(
        f"{easee.sr_base}/negotiate",
        payload={"connectionId": "abc-123"},
    )

    client = SignalRClient(easee.sr_base, headers=easee.sr_headers)
    await client._transport._negotiate()

    assert "Cookie" not in client._transport._headers

    await easee.close()
    await aiosession.close()
