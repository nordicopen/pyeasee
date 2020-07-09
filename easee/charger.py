import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Union, cast

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


class Charger:
    def __init__(self, id: str, name: str, easee: Any):
        self.id: str = id
        self.name: str = name
        self.easee = easee
        self._state: Dict[str, Any] = {}
        self._config: Dict[str, Any] = {}

    async def get_consumption_between_dates(self, from_date: datetime, to_date):
        """ Gets consumption between two dates """
        value = await (
            await self.easee.get(
                f"/api/sessions/charger/{self.id}/total/{from_date.isoformat()}/{to_date.isoformat()}"
            )
        ).text()
        return float(value)

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
            self._config = {
                **config,
                "localNodeType": NODE_TYPE[config["localNodeType"]],
                "phaseMode": PHASE_MODE[config["phaseMode"]],
            }
        return self._config

    async def get_state(self, from_cache=False):
        """ get state for charger """
        if not from_cache:
            state = await (await self.easee.get(f"/api/chargers/{self.id}/state")).json()
            self._state = {
                **state,
                "chargerOpMode": STATUS[state["chargerOpMode"]],
            }
        return self._state

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
        return await self.easee.post(
            f"/api/chargers/{self.id}/commands/basic_charge_plan", json=json
        )

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

    async def async_update(self):
        """ Convienient method to update both config and state """
        self._state = await self.get_state()
        self._config = await self.get_config()

        _LOGGER.debug(
            "Charger:\n %s\n\nState:\n %s\n\nConfig: %s", self.name, self._state, self._config
        )
