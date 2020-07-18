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


@pytest.mark.asyncio
async def test_get_chargers():
    session = aiohttp.ClientSession()
    with aioresponses() as m:
        token_data = load_json_fixture("token.json")
        m.post(f"{BASE_URL}/api/accounts/token", payload=token_data)

        chargers_data = load_json_fixture("chargers.json")
        m.get(f"{BASE_URL}/api/chargers", payload=chargers_data)

        easee = Easee("+46070123456", "password", session)
        chargers = await easee.get_chargers()
        assert chargers[0].id == "EH12345"

        chargers_state_data = load_json_fixture("charger-state.json")
        m.get(f"{BASE_URL}/api/chargers/EH12345/state", payload=chargers_state_data)

        state = await chargers[0].get_state()
        assert state["chargerOpMode"] == "PAUSED"
        await easee.close()

