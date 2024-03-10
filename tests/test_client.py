import asyncio
import json
import os

import aiohttp
import pytest
import pytest_asyncio
from aioresponses import aioresponses
from pyeasee import Charger, Easee

BASE_URL = "https://api.easee.com"


def load_json_fixture(filename):
    with open(os.path.join(os.path.dirname(__file__), "fixtures", filename)) as f:
        return json.load(f)


@pytest_asyncio.fixture
async def aioresponse():
    with aioresponses() as m:
        yield m


@pytest_asyncio.fixture
async def aiosession():
    return aiohttp.ClientSession()


@pytest.mark.asyncio
async def test_get_chargers(aiosession, aioresponse):

    token_data = load_json_fixture("token.json")
    aioresponse.post(f"{BASE_URL}/api/accounts/login", payload=token_data)

    chargers_data = load_json_fixture("chargers.json")
    aioresponse.get(f"{BASE_URL}/api/chargers", payload=chargers_data)

    easee = Easee("+46070123456", "password", aiosession)
    chargers = await easee.get_chargers()
    assert chargers[0].id == "EH12345"

    chargers_state_data = load_json_fixture("charger-state.json")
    aioresponse.get(f"{BASE_URL}/api/chargers/EH12345/state", payload=chargers_state_data)

    state = await chargers[0].get_state(raw=True)

    assert state["chargerOpMode"] == 2

    await easee.close()
    await aiosession.close()


@pytest.mark.asyncio
async def test_get_sites(aiosession, aioresponse):

    token_data = load_json_fixture("token.json")
    aioresponse.post(f"{BASE_URL}/api/accounts/login", payload=token_data)

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


@pytest.mark.asyncio
async def test_get_site_state(aiosession, aioresponse):

    token_data = load_json_fixture("token.json")
    aioresponse.post(f"{BASE_URL}/api/accounts/login", payload=token_data)

    site_state_data = load_json_fixture("site-state.json")
    aioresponse.get(f"{BASE_URL}/api/sites/54321/state", payload=site_state_data)

    easee = Easee("+46070123456", "password", aiosession)
    site_state = await easee.get_site_state("54321")

    charger_config = site_state.get_charger_config("EH123497")
    assert charger_config["localNodeType"] == "Master"

    charger_state = site_state.get_charger_state("EH123497", raw=True)

    assert charger_state["chargerOpMode"] == 1


    charger_state = site_state.get_charger_state("NOTEXIST")
    assert charger_state is None

    await easee.close()
    await aiosession.close()
