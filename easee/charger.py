import logging
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Union, cast

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
    0: "(0) No reason, charging or ready to charge",
    50: "(50) Secondary unit not requesting current or no car connected",
    52: "(52) Charger paused",
    53: "(53) Charger disabled",
}


class ChargerState(BaseDict):
    def __init__(self, entries: Dict[str, Any], easee: Any):
        super().__init__(entries)
        self.easee = easee


class ChargerConfig(BaseDict):
    def __init__(self, entries: Dict[str, Any], easee: Any):
        super().__init__(entries)
        self.easee = easee


class Charger(BaseDict):
    def __init__(self, entries: Dict[str, Any], circuit: Any, easee: Any):
        super().__init__(entries)
        self.id: str = entries["id"]
        self.name: str = entries["name"]
        self.easee = easee
        self.circuit = circuit
        self._config: ChargerConfig({}, easee)
        self._state: ChargerState({}, easee)

    async def get_consumption_between_dates(self, from_date: datetime, to_date):
        """ Gets consumption between two dates """
        value = await (
            await self.easee.get(
                f"/api/sessions/charger/{self.id}/total/{from_date.isoformat()}/{to_date.isoformat()}"
            )
        ).text()
        return float(value)

    def get_name(self):
        return self.name

    def get_cached_config_entry(self, key):
        """ Get cached config entry """
        return self._config[key]

    def get_cached_state_entry(self, key):
        """ Get cached config entry """
        return self._state[key]

    async def get_config(self, from_cache=False):
        """ get config for charger """
        if not from_cache:
            config = await (await self.easee.get(f"/api/chargers/{self.id}/config")).json()
            self._config = ChargerConfig(
                {
                    **config,
                    "localNodeType": NODE_TYPE[config["localNodeType"]],
                    "phaseMode": PHASE_MODE[config["phaseMode"]],
                },
                self.easee,
            )
        return self._config

    async def get_state(self, from_cache=False):
        """ get state for charger """
        if not from_cache:
            state = await (await self.easee.get(f"/api/chargers/{self.id}/state")).json()
            self._state = ChargerState(
                {
                    **state,
                    "chargerOpMode": STATUS[state["chargerOpMode"]],
                    "reasonForNoCurrent": REASON_FOR_NO_CURRENT.get(state["reasonForNoCurrent"], "Unknown"),
                },
                self.easee,
            )
        return self._state

    def get_data(self):
        return (
            {**self._storage, "state": self._state.get_data(), "config": self._config.get_data()},
        )

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

    async def get_basic_charge_plan(self):
        """Get and return charger basic charge plan setting from cloud """
        return await self.easee.get(f"/api/chargers/{self.id}/commands/basic_charge_plan")

    async def set_basic_charge_plan(self, id, chargeStartTime, chargeStopTime, repeat=True):
        """Set and post charger basic charge plan setting to cloud """
        json = {
            "id": id,
            "chargeStartTime": chargeStartTime,
            "chargeStopTime": chargeStopTime,
            "repeat": repeat,
        }
        return await self.easee.post(f"/api/chargers/{self.id}/commands/basic_charge_plan", json=json)

    async def delete_basic_charge_plan(self):
        """Delete charger basic charge plan setting from cloud """
        return await self.easee.post(f"/api/chargers/{self.id}/commands/basic_charge_plan")

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

    async def set_circuit_maxcurrent(self, maxCircuitCurrent):
        """ Set max current settings for charger circuit """
        return await self.circuit.set_circuit_maxcurrent(maxCircuitCurrent)

    async def set_circuit_dynamicCurrent(self, dynamicCircuitCurrent):
        """ Set dynamic current settings for charger circuit """
        return await self.circuit.set_circuit_dynamicCurrent(dynamicCircuitCurrent)

    async def async_update(self):
        """ Convienient method to update both config and state """
        self._state = await self.get_state()
        self._config = await self.get_config()

        _LOGGER.debug(
            "Charger:\n %s\n\nState:\n %s\n\nConfig: %s", self.id, self._state, self._config
        )
