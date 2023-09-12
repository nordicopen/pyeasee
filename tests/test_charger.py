import pytest
from pyeasee import Charger


class MockResponse:
    def __init__(self, data):
        self.data = data

    async def json(self):
        return self.data


class MockEasee:
    def __init__(self, get_data={}, post_data={}):
        self.get_data = get_data
        self.post_data = post_data

    async def post(self, url, **kwargs):
        return MockResponse(self.post_data)

    async def get(self, url, **kwargs):
        return MockResponse(self.get_data)


default_state = {
    "smartCharging": False,
    "cableLocked": False,
    "chargerOpMode": 3,
    "totalPower": 0.0,
    "sessionEnergy": 5.587664604187012,
    "energyPerHour": 0.0,
    "wiFiRSSI": -66,
    "cellRSSI": -73,
    "localRSSI": None,
    "outputPhase": 0,
    "dynamicCircuitCurrentP1": 40.0,
    "dynamicCircuitCurrentP2": 40.0,
    "dynamicCircuitCurrentP3": 40.0,
    "latestPulse": "2020-07-09T11:37:37Z",
    "chargerFirmware": 230,
    "latestFirmware": 230,
    "voltage": 241.61900329589844,
    "chargerRAT": 1,
    "lockCablePermanently": False,
    "inCurrentT2": 0.0,
    "inCurrentT3": 0.0,
    "inCurrentT4": 0.0,
    "inCurrentT5": 0.0,
    "outputCurrent": 0.0,
    "isOnline": True,
    "inVoltageT1T2": 3.0850000381469727,
    "inVoltageT1T3": 241.29299926757812,
    "inVoltageT1T4": 235.20799255371094,
    "inVoltageT1T5": 235.1269989013672,
    "inVoltageT2T3": 241.61900329589844,
    "inVoltageT2T4": 237.75399780273438,
    "inVoltageT2T5": 232.3679962158203,
    "inVoltageT3T4": 408.0639953613281,
    "inVoltageT3T5": 414.3399963378906,
    "inVoltageT4T5": 410.01800537109375,
    "ledMode": 18,
    "cableRating": 20000.0,
    "dynamicChargerCurrent": 32.0,
    "circuitTotalAllocatedPhaseConductorCurrentL1": None,
    "circuitTotalAllocatedPhaseConductorCurrentL2": None,
    "circuitTotalAllocatedPhaseConductorCurrentL3": None,
    "circuitTotalPhaseConductorCurrentL1": 0.0,
    "circuitTotalPhaseConductorCurrentL2": 0.0,
    "circuitTotalPhaseConductorCurrentL3": 0.0,
    "reasonForNoCurrent": 50,
    "wiFiAPEnabled": False,
}

default_config = {
    "isEnabled": True,
    "lockCablePermanently": False,
    "authorizationRequired": False,
    "remoteStartRequired": True,
    "smartButtonEnabled": False,
    "wiFiSSID": "wifi ssid",
    "detectedPowerGridType": 1,
    "offlineChargingMode": 0,
    "circuitMaxCurrentP1": 16.0,
    "circuitMaxCurrentP2": 16.0,
    "circuitMaxCurrentP3": 16.0,
    "enableIdleCurrent": False,
    "limitToSinglePhaseCharging": None,
    "phaseMode": 3,
    "localNodeType": 1,
    "localAuthorizationRequired": False,
    "localRadioChannel": 7,
    "localShortAddress": 0,
    "localParentAddrOrNumOfNodes": 0,
    "localPreAuthorizeEnabled": None,
    "localAuthorizeOfflineEnabled": None,
    "allowOfflineTxForUnknownId": None,
    "maxChargerCurrent": 32.0,
    "ledStripBrightness": None,
}


@pytest.mark.asyncio
async def test_get_correct_status():
    mock_easee = MockEasee(get_data=default_state)
    charger = Charger({"id": "EH123456", "name": "Easee Home 12345", "productCode": 1, "userRole": 1, "levelOfAccess": 1}, mock_easee)
    state = await charger.get_state(raw=True)
    assert state["chargerOpMode"] == 3


@pytest.mark.asyncio
async def test_get_correct_phase_mode():
    mock_easee = MockEasee(get_data=default_config)
    charger = Charger({"id": "EH123456", "name": "Easee Home 12345", "productCode": 1, "userRole": 1, "levelOfAccess": 1}, mock_easee)
    state = await charger.get_config()
    assert state["phaseMode"] == "Locked to three phase"
