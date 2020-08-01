import os
import json
import pytest
import asyncio
import aiohttp
from aioresponses import aioresponses

from easee import Easee, Charger

BASE_URL = "https://api.easee.cloud"


def load_json_fixture(filename):
    with open(os.path.join(os.path.dirname(__file__), "fixtures", filename)) as f:
        return json.load(f)


@pytest.fixture
def aioresponse():
    with aioresponses() as m:
        yield m


@pytest.fixture
async def aiosession():
    return aiohttp.ClientSession()


@pytest.mark.asyncio
async def test_get_chargers(aiosession, aioresponse):

    token_data = load_json_fixture("token.json")
    aioresponse.post(f"{BASE_URL}/api/accounts/token", payload=token_data)

    chargers_data = load_json_fixture("chargers.json")
    aioresponse.get(f"{BASE_URL}/api/chargers", payload=chargers_data)

    easee = Easee("+46070123456", "password", aiosession)
    chargers = await easee.get_chargers()
    assert chargers[0].id == "EH12345"

    chargers_state_data = load_json_fixture("charger-state.json")
    aioresponse.get(f"{BASE_URL}/api/chargers/EH12345/state", payload=chargers_state_data)

    state = await chargers[0].get_state()
    assert state["chargerOpMode"] == "PAUSED"
    await easee.close()
    await aiosession.close()


@pytest.mark.asyncio
async def test_get_sites(aiosession, aioresponse):

    token_data = load_json_fixture("token.json")
    aioresponse.post(f"{BASE_URL}/api/accounts/token", payload=token_data)

    sites_data = load_json_fixture("sites.json")
    aioresponse.get(f"{BASE_URL}/api/sites", payload=sites_data)

    site_data = load_json_fixture("site.json")
    aioresponse.get(f"{BASE_URL}/api/sites/55555?detailed=true", payload=site_data)

    easee = Easee("+46070123456", "password", aiosession)
    sites = await easee.get_sites()

    assert sites[0].id == 55555

    circuits = sites[0].get_circuits()
    assert circuits[0].id == 12345

    chargers_data = load_json_fixture("chargers.json")
    aioresponse.get(f"{BASE_URL}/api/chargers", payload=chargers_data)

    chargers = circuits[0].get_chargers()

    assert chargers[0].id == "ES12345"
    await easee.close()
    await aiosession.close()

