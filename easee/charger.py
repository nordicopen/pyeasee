import logging
from datetime import datetime
from typing import Any, Dict

from .exceptions import NotFoundException
from .utils import BaseDict

_LOGGER = logging.getLogger(__name__)

STATUS = {
    1: "STANDBY",
    2: "PAUSED",
    3: "CHARGING",
    4: "READY_TO_CHARGE",
    5: "UNKNOWN",
    6: "CAR_CONNECTED",
}

NODE_TYPE = {
    1: "Master",
    2: "Extender",
}

PHASE_MODE = {
    1: "Locked to single phase",
    2: "Auto",
    3: "Locked to three phase",
}

REASON_FOR_NO_CURRENT = {
    # Work-in-progress, must be taken with a pinch of salt, as per now just reverse engineering of observations until API properly documented
    None: "No reason",
    0: "No reason, charging or ready to charge",
    50: "Secondary unit not requesting current or no car connected",
    52: "Charger paused",
    53: "Charger disabled",
    54: "Waiting for schedule",
}


class ChargerState(BaseDict):
    """ Charger state with integer enum values converted to human readable string values"""

    def __init__(self, state: Dict[str, Any]):
        data = {
            **state,
            "chargerOpMode": STATUS[state["chargerOpMode"]],
            "reasonForNoCurrent": f"({state['reasonForNoCurrent']}) {REASON_FOR_NO_CURRENT.get(state['reasonForNoCurrent'], 'Unknown')}",
        }
        super().__init__(data)


class ChargerConfig(BaseDict):
    """ Charger config with integer enum values converted to human readable string values"""

    def __init__(self, config: Dict[str, Any]):
        data = {
            **config,
            "localNodeType": NODE_TYPE[config["localNodeType"]],
            "phaseMode": PHASE_MODE[config["phaseMode"]],
        }
        super().__init__(data)


class ChargerSchedule(BaseDict):
    """ Charger charging schedule/plan """

    def __init__(self, schedule: Dict[str, Any]):
        # Todo remove the False defaults. Either it is a schedule object or None
        data = {
            "id": schedule.get("id", False),
            "chargeStartTime": schedule.get("chargeStartTime", False),
            "chargeStopTime": schedule.get("chargeStopTime", False),
            "repeat": schedule.get("repeat", False),
        }
        super().__init__(data)


class Charger(BaseDict):
    def __init__(self, entries: Dict[str, Any], easee: Any, site: Any = None, circuit: Any = None):
        super().__init__(entries)
        self.id: str = entries["id"]
        self.name: str = entries["name"]
        self.site = site
        self.circuit = circuit
        self.easee = easee

    async def get_consumption_between_dates(self, from_date: datetime, to_date):
        """ Gets consumption between two dates """
        value = await (
            await self.easee.get(f"/api/sessions/charger/{self.id}/total/{from_date.isoformat()}/{to_date.isoformat()}")
        ).text()
        return float(value)

    async def get_config(self, from_cache=False) -> ChargerConfig:
        """ get config for charger """
        config = await (await self.easee.get(f"/api/chargers/{self.id}/config")).json()
        return ChargerConfig(config)

    async def get_state(self) -> ChargerState:
        """ get state for charger """
        state = await (await self.easee.get(f"/api/chargers/{self.id}/state")).json()
        return ChargerState(state)

    async def start(self):
        """Start charging session"""
        return await self.easee.post(f"/api/chargers/{self.id}/commands/start_charging")

    async def pause(self):
        """Pause charging session"""
        return await self.easee.post(f"/api/chargers/{self.id}/commands/pause_charging")

    async def resume(self):
        """Resume charging session"""
        return await self.easee.post(f"/api/chargers/{self.id}/commands/resume_charging")

    async def stop(self):
        """Stop charging session"""
        return await self.easee.post(f"/api/chargers/{self.id}/commands/stop_charging")

    async def toggle(self):
        """Toggle charging session start/stop/pause/resume """
        return await self.easee.post(f"/api/chargers/{self.id}/commands/toggle_charging")

    async def get_basic_charge_plan(self) -> ChargerSchedule:
        """Get and return charger basic charge plan setting from cloud """
        plan = await self.easee.get(f"/api/chargers/{self.id}/basic_charge_plan")
        try:
            plan = await plan.json()
            _LOGGER.debug(plan)
        except NotFoundException:
            # TODO: fix me. Should return None here instead of a ChargerSchedule with False as id
            plan = {"id": False}
            _LOGGER.debug("No scheduled charge plan")
        return ChargerSchedule(plan)

    # TODO: document types
    async def set_basic_charge_plan(self, id, chargeStartTime, chargeStopTime, repeat=True):
        """Set and post charger basic charge plan setting to cloud """
        json = {
            "id": id,
            "chargeStartTime": str(chargeStartTime),
            "chargeStopTime": str(chargeStopTime),
            "repeat": repeat,
        }
        return await self.easee.post(f"/api/chargers/{self.id}/basic_charge_plan", json=json)

    async def delete_basic_charge_plan(self):
        """Delete charger basic charge plan setting from cloud """
        return await self.easee.delete(f"/api/chargers/{self.id}/basic_charge_plan")

    async def override_schedule(self):
        """Override scheduled charging and start charging"""
        return await self.easee.post(f"/api/chargers/{self.id}/commands/override_schedule")

    async def smart_charging(self):
        """Set charger smart charging setting"""
        return await self.easee.post(f"/api/chargers/{self.id}/commands/smart_charging")

    async def reboot(self):
        """Reboot charger"""
        return await self.easee.post(f"/api/chargers/{self.id}/commands/reboot")

    async def update_firmware(self):
        """Update charger firmware"""
        return await self.easee.post(f"/api/chargers/{self.id}/commands/update_firmware")

    async def set_dynamic_current(self, currentP1: int, currentP2: int = None, currentP3: int = None):
        """ Set circuit dynamic current for charger """
        if self.circuit is not None:
            return await self.circuit.set_dynamic_current(currentP1, currentP2, currentP3)
        else:
            _LOGGER.info("Circuit info must be initialized for dynamic current to be set")

    async def set_max_current(self, currentP1: int, currentP2: int = None, currentP3: int = None):
        """ Set circuit max current for charger """
        if self.circuit is not None:
            return await self.circuit.set_max_current(currentP1, currentP2, currentP3)
        else:
            _LOGGER.info("Circuit info must be initialized for max current to be set")
