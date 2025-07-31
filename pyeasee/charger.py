from datetime import datetime, timezone
import logging
from typing import Any, Dict, Union

from .exceptions import NotFoundException, ServerFailureException
from .throttler import Throttler
from .utils import BaseDict

_LOGGER = logging.getLogger(__name__)


STATUS = {
    0: "OFFLINE",
    1: "DISCONNECTED",
    2: "AWAITING_START",
    3: "CHARGING",
    4: "COMPLETED",
    5: "ERROR",
    6: "READY_TO_CHARGE",
    7: "AWAITING_AUTHORIZATION",
    8: "DE_AUTHORIZING",
    100: "START_CHARGING",
    101: "STOP_CHARGING",
    102: "OFFLINE",
    103: "AWAITING_LOAD_BALANCING",
    104: "AWAITING_AUTHORIZATION",
    105: "AWAITING_SMART_START",
    106: "AWAITING_SCHEDULED_START",
    107: "AUTHENTICATING",
    108: "PAUSED_DUE_TO_EQUALIZER",
    109: "SEARCHING_FOR_MASTER",
    157: "ERRATIC_EV",
    158: "ERROR_TEMPERATURE_TOO_HIGH",
    159: "ERROR_DEAD_POWERBOARD",
    160: "ERROR_OVERCURRENT",
    161: "ERROR_PEN_FAULT",
}

NODE_TYPE = {1: "Master", 2: "Extender"}

PHASE_MODE = {1: "Locked to single phase", 2: "Auto", 3: "Locked to three phase"}

REASON_FOR_NO_CURRENT = {
    # Work-in-progress, must be taken with a pinch of salt, as per now just reverse engineering of observations until API properly documented
    None: "No reason",
    0: "No reason, charging or ready to charge",
    1: "Max circuit limit too low",
    2: "Max dynamic circuit limit too low",
    3: "Max dynamic offline limit too low",
    4: "Circuit fuse too low",
    5: "Waiting in queue",
    6: "Waiting in fully",
    7: "Illegal grid type",
    8: "No current request recieved",
    9: "Not connected to master",
    10: "EQ current too low",
    11: "Phase not connected",
    25: "Limited by circuit fuse",
    26: "Limited by circuit max limit",
    27: "Limited by circuit dynamic limit",
    28: "Limited by equalizer",
    29: "Limited by load balancing",
    30: "Limited by offline settings",
    50: "Secondary unit not requesting current or no car connected",
    51: "Max charger limit too low",
    52: "Max dynamic charger limit too low",
    53: "Charger disabled",
    54: "Waiting for schedule/auth",
    55: "Pending auth",
    56: "Charger in error state",
    57: "EV erratic",
    75: "Limited by cable rating",
    76: "Limited by schedule",
    77: "Limited by charger max limit",
    78: "Limited by charger dynamic limit",
    79: "EV is not charging",
    80: "Limited by local adjustment",
    81: "Limited by EV",
    100: "Undefined",
}


class ChargerState(BaseDict):
    """Charger state with integer enum values converted to human readable string values"""

    def __init__(self, state: Dict[str, Any], raw=False):
        if not raw:
            data = {
                **state,
                "chargerOpMode": STATUS[state["chargerOpMode"]],
                "reasonForNoCurrent": f"({state['reasonForNoCurrent']}) {REASON_FOR_NO_CURRENT.get(state['reasonForNoCurrent'], 'Unknown')}",
            }
        else:
            data = {
                **state,
                "reasonForNoCurrent": "none" if state["reasonForNoCurrent"] is None else state["reasonForNoCurrent"],
            }
        super().__init__(data)


class ChargerConfig(BaseDict):
    """Charger config with integer enum values converted to human readable string values"""

    def __init__(self, config: Dict[str, Any], raw=False):
        if not raw:
            data = {
                **config,
                "localNodeType": NODE_TYPE[config["localNodeType"]],
                "phaseMode": PHASE_MODE[config["phaseMode"]],
            }
        else:
            data = {**config}
        super().__init__(data)


class ChargerSchedule(BaseDict):
    """Charger charging schedule/plan"""

    def __init__(self, schedule: Dict[str, Any]):
        data = {
            "id": schedule.get("id"),
            "chargeStartTime": schedule.get("chargeStartTime"),
            "chargeStopTime": schedule.get("chargeStopTime"),
            "repeat": schedule.get("repeat"),
            "isEnabled": schedule.get("isEnabled"),
            "chargingCurrentLimit": schedule.get("chargingCurrentLimit"),
        }
        super().__init__(data)


class ChargerWeeklySchedule(BaseDict):
    """Charger charging schedule/plan"""

    def __init__(self, schedule: Dict[str, Any]):
        days = schedule.get("days")
        data = {
            "isEnabled": schedule.get("isEnabled"),
            "MondayStartTime": "-",
            "MondayStopTime": "-",
            "TuesdayStartTime": "-",
            "TuesdayStopTime": "-",
            "WednesdayStartTime": "-",
            "WednesdayStopTime": "-",
            "ThursdayStartTime": "-",
            "ThursdayStopTime": "-",
            "FridayStartTime": "-",
            "FridayStopTime": "-",
            "SaturdayStartTime": "-",
            "SaturdayStopTime": "-",
            "SundayStartTime": "-",
            "SundayStopTime": "-",
            "days": days,
        }
        if data["isEnabled"]:
            tzinfo = datetime.utcnow().astimezone().tzinfo
            for day in days:
                ranges = day["ranges"]
                for times in ranges:
                    limit = times["chargingCurrentLimit"]
                    try:
                        start = (
                            datetime.strptime(times["startTime"], "%H:%MZ")
                            .replace(tzinfo=timezone.utc)
                            .astimezone(tzinfo)
                            .strftime("%H:%M")
                        )
                        stop = (
                            datetime.strptime(times["stopTime"], "%H:%MZ")
                            .replace(tzinfo=timezone.utc)
                            .astimezone(tzinfo)
                            .strftime("%H:%M")
                        )
                    except ValueError:
                        start = (
                            datetime.strptime(times["startTime"], "%H:%M")
                            .replace(tzinfo=timezone.utc)
                            .astimezone(tzinfo)
                            .strftime("%H:%M")
                        )
                        stop = (
                            datetime.strptime(times["stopTime"], "%H:%M")
                            .replace(tzinfo=timezone.utc)
                            .astimezone(tzinfo)
                            .strftime("%H:%M")
                        )

                    if day["dayOfWeek"] == 0:
                        data["MondayStartTime"] = start
                        data["MondayStopTime"] = stop
                        data["MondayLimit"] = limit
                    elif day["dayOfWeek"] == 1:
                        data["TuesdayStartTime"] = start
                        data["TuesdayStopTime"] = stop
                        data["TuesdayLimit"] = limit
                    elif day["dayOfWeek"] == 2:
                        data["WednesdayStartTime"] = start
                        data["WednesdayStopTime"] = stop
                        data["WednesdayLimit"] = limit
                    elif day["dayOfWeek"] == 3:
                        data["ThursdayStartTime"] = start
                        data["ThursdayStopTime"] = stop
                        data["ThursdayLimit"] = limit
                    elif day["dayOfWeek"] == 4:
                        data["FridayStartTime"] = start
                        data["FridayStopTime"] = stop
                        data["FridayLimit"] = limit
                    elif day["dayOfWeek"] == 5:
                        data["SaturdayStartTime"] = start
                        data["SaturdayStopTime"] = stop
                        data["SaturdayLimit"] = limit
                    elif day["dayOfWeek"] == 6:
                        data["SundayStartTime"] = start
                        data["SundayStopTime"] = stop
                        data["SundayLimit"] = limit

        super().__init__(data)


class ChargerSession(BaseDict):
    """Charger charging session"""

    def __init__(self, session: Dict[str, Any]):
        data = {
            "carConnected": session.get("carConnected"),
            "carDisconnected": session.get("carDisconnected"),
            "kiloWattHours": float(session.get("kiloWattHours")),
        }
        super().__init__(data)


class Charger(BaseDict):
    def __init__(self, entries: Dict[str, Any], easee: Any, site: Any = None, circuit: Any = None):
        super().__init__(entries)
        self.id: str = entries["id"]
        self.name: str = entries["name"]
        self.product_code: int = entries["productCode"]
        self.level_of_access: int = entries["levelOfAccess"]
        self.user_role: int = entries.get("userRole", -1)
        self.site = site
        self.circuit = circuit
        self.easee = easee
        self._consumption_between_dates_throttler = Throttler(
            rate_limit=10, period=3600, name="consumption between dates"
        )
        self._sessions_between_dates_throttler = Throttler(rate_limit=10, period=3600, name="sessions between dates")

    async def get_observations(self, *args):
        """Gets observation IDs"""
        observation_ids = ",".join(str(s) for s in args)
        try:
            return await (await self.easee.get(f"/state/{self.id}/observations?ids={observation_ids}")).json()
        except (ServerFailureException):
            return None

    async def get_consumption_between_dates(self, from_date: datetime, to_date):
        """Gets consumption between two dates"""
        try:
            async with self._consumption_between_dates_throttler:
                value = await (
                    await self.easee.get(
                        f"/api/sessions/charger/{self.id}/total/{from_date.isoformat()}/{to_date.isoformat()}"
                    )
                ).text()
                return float(value)
        except (ServerFailureException):
            return None

    async def get_hourly_consumption_between_dates(self, from_date: datetime, to_date: datetime):
        """Gets hourly consumption between two dates
        Note when calling: Seems to be capped at requesting max one month at a time
        """
        try:
            value = await (
                await self.easee.get(
                    f"/api/chargers/{self.id}/usage/hourly/{from_date.isoformat()}/{to_date.isoformat()}"
                )
            ).json()
            return value
        except (ServerFailureException):
            return None

    async def get_sessions_between_dates(self, from_date: datetime, to_date):
        """Gets charging sessions between two dates"""
        try:
            async with self._sessions_between_dates_throttler:
                sessions = await (
                    await self.easee.get(
                        f"/api/sessions/charger/{self.id}/sessions/{from_date.isoformat()}/{to_date.isoformat()}"
                    )
                ).json()
                sessions = [ChargerSession(session) for session in sessions]
                sessions.sort(key=lambda x: x["carConnected"], reverse=True)
                return sessions
        except (ServerFailureException):
            return None

    async def get_config(self, from_cache=False, raw=False) -> ChargerConfig:
        """get config for charger"""
        try:
            config = await (await self.easee.get(f"/api/chargers/{self.id}/config")).json()
            return ChargerConfig(config, raw)
        except (ServerFailureException):
            return None

    async def get_state(self, raw=False) -> ChargerState:
        """get state for charger"""
        try:
            state = await (await self.easee.get(f"/api/chargers/{self.id}/state")).json()
            return ChargerState(state, raw)
        except (ServerFailureException):
            return None

    async def empty_config(self, raw=False) -> ChargerConfig:
        """Create an empty config data structure"""
        config = {}
        return ChargerConfig(config, raw)

    async def empty_state(self, raw=False) -> ChargerConfig:
        """Create an empty config data structure"""
        state = {
            "chargerOpMode": 0,
            "reasonForNoCurrent": 0,
        }
        return ChargerState(state, raw)

    async def start(self):
        """Start charging session"""
        try:
            return await self.easee.post(f"/api/chargers/{self.id}/commands/start_charging")
        except (ServerFailureException):
            return None

    async def pause(self):
        """Pause charging session"""
        try:
            return await self.easee.post(f"/api/chargers/{self.id}/commands/pause_charging")
        except (ServerFailureException):
            return None

    async def resume(self):
        """Resume charging session"""
        try:
            return await self.easee.post(f"/api/chargers/{self.id}/commands/resume_charging")
        except (ServerFailureException):
            return None

    async def stop(self):
        """Stop charging session"""
        try:
            return await self.easee.post(f"/api/chargers/{self.id}/commands/stop_charging")
        except (ServerFailureException):
            return None

    async def toggle(self):
        """Toggle charging session start/stop/pause/resume"""
        try:
            return await self.easee.post(f"/api/chargers/{self.id}/commands/toggle_charging")
        except (ServerFailureException):
            return None

    async def get_basic_charge_plan(self) -> ChargerSchedule:
        """Get and return charger basic charge plan setting from cloud"""
        try:
            plan = await self.easee.get(f"/api/chargers/{self.id}/basic_charge_plan")
            plan = await plan.json()
            return ChargerSchedule(plan)
        except (NotFoundException):
            _LOGGER.debug("No scheduled charge plan")
            return None
        except (ServerFailureException):
            return None

    # TODO: document types
    async def set_basic_charge_plan(
        self, id, chargeStartTime, chargeStopTime=None, repeat=True, isEnabled=True, limit=32
    ):
        """Set and post charger basic charge plan setting to cloud"""
        json = {
            "id": id,
            "chargeStartTime": str(chargeStartTime),
            "repeat": repeat,
            "isEnabled": isEnabled,
            "chargingCurrentLimit": limit,
        }
        if chargeStopTime is not None:
            json["chargeStopTime"] = str(chargeStopTime)

        try:
            return await self.easee.post(f"/api/chargers/{self.id}/basic_charge_plan", json=json)
        except (ServerFailureException):
            return None

    async def disable_basic_charge_plan(self):
        await self.enable_basic_charge_plan(False)

    async def enable_basic_charge_plan(self, enable=True):
        """Enabled or disable basic charge plan without changing other settings."""

        try:
            plan = await self.easee.get(f"/api/chargers/{self.id}/basic_charge_plan")
            plan = await plan.json()
        except (NotFoundException):
            _LOGGER.debug("No scheduled charge plan")
            plan = None
        except (ServerFailureException):
            plan = None

        if plan is not None:
            plan["isEnabled"] = enable
            json = plan

            try:
                return await self.easee.post(f"/api/chargers/{self.id}/basic_charge_plan", json=json)
            except (ServerFailureException):
                return None

    async def get_weekly_charge_plan(self) -> ChargerWeeklySchedule:
        """Get and return charger weekly charge plan setting from cloud"""
        try:
            plan = await self.easee.get(f"/api/chargers/{self.id}/weekly_charge_plan")
            plan = await plan.json()
            _LOGGER.debug(plan)
            return ChargerWeeklySchedule(plan)
        except (NotFoundException):
            _LOGGER.debug("No scheduled charge plan")
            return None
        except (ServerFailureException):
            return None

    # TODO: document types
    async def set_weekly_charge_plan(self, day, chargeStartTime, chargeStopTime, enabled=True, limit=32):
        """Set and post charger weekly charge plan setting to cloud"""

        try:
            plan = await self.easee.get(f"/api/chargers/{self.id}/weekly_charge_plan")
            plan = await plan.json()
            _LOGGER.debug(plan)
        except (NotFoundException):
            _LOGGER.debug("No scheduled charge plan")
            plan = None
        except (ServerFailureException):
            return None

        if plan is None:
            json = {
                "isEnabled": enabled,
                "days": [
                    {
                        "dayOfWeek": day,
                        "ranges": [
                            {
                                "startTime": str(chargeStartTime),
                                "stopTime": str(chargeStopTime),
                                "chargingCurrentLimit": limit,
                            }
                        ],
                    }
                ],
            }
        else:
            json = plan
            json["isEnabled"] = enabled
            days = json["days"]
            newdays = []
            for oldday in days:
                if oldday["dayOfWeek"] == day:
                    newday = {
                        "dayOfWeek": day,
                        "ranges": [
                            {
                                "startTime": str(chargeStartTime),
                                "stopTime": str(chargeStopTime),
                                "chargingCurrentLimit": limit,
                            }
                        ],
                    }
                    newdays.append(newday)
                else:
                    newdays.append(oldday)
            json["days"] = newdays

        try:
            return await self.easee.post(f"/api/chargers/{self.id}/weekly_charge_plan", json=json)
        except (ServerFailureException):
            return None

    async def disable_weekly_charge_plan(self):
        await self.enable_weekly_charge_plan(False)

    async def enable_weekly_charge_plan(self, enable=True):
        """Enable or disable charger weekly charge plan setting to cloud"""

        try:
            plan = await self.easee.get(f"/api/chargers/{self.id}/weekly_charge_plan")
            plan = await plan.json()
            _LOGGER.debug(plan)
        except (NotFoundException):
            _LOGGER.debug("No scheduled charge plan")
            plan = None
        except (ServerFailureException):
            return None

        if plan is not None:
            json = plan
            json["isEnabled"] = enable

            try:
                return await self.easee.post(f"/api/chargers/{self.id}/weekly_charge_plan", json=json)
            except (ServerFailureException):
                return None

    async def enable_charger(self, enable: bool):
        """Enable and disable charger in charger settings"""
        json = {"enabled": enable}
        try:
            return await self.easee.post(f"/api/chargers/{self.id}/settings", json=json)
        except (ServerFailureException):
            return None

    async def enable_idle_current(self, enable: bool):
        """Enable and disable idle current in charger settings"""
        json = {"enableIdleCurrent": enable}
        try:
            return await self.easee.post(f"/api/chargers/{self.id}/settings", json=json)
        except (ServerFailureException):
            return None

    async def limitToSinglePhaseCharging(self, enable: bool):
        """Limit to single phase charging in charger settings"""
        json = {"limitToSinglePhaseCharging": enable}
        try:
            return await self.easee.post(f"/api/chargers/{self.id}/settings", json=json)
        except (ServerFailureException):
            return None

    async def phaseMode(self, mode: int = 2):
        """Set charging phase mode, 1 = always 1-phase, 2 = auto, 3 = always 3-phase"""
        json = {"phaseMode": mode}
        try:
            return await self.easee.post(f"/api/chargers/{self.id}/settings", json=json)
        except (ServerFailureException):
            return None

    async def lockCablePermanently(self, enable: bool):
        """Lock and unlock cable permanently in charger settings"""
        json = {"state": enable}
        try:
            return await self.easee.post(f"/api/chargers/{self.id}/commands/lock_state", json=json)
        except (ServerFailureException):
            return None

    async def smartButtonEnabled(self, enable: bool):
        """Enable and disable smart button in charger settings"""
        json = {"smartButtonEnabled": enable}
        try:
            return await self.easee.post(f"/api/chargers/{self.id}/settings", json=json)
        except (ServerFailureException):
            return None

    async def delete_basic_charge_plan(self):
        """Delete charger basic charge plan setting from cloud"""
        try:
            return await self.easee.delete(f"/api/chargers/{self.id}/basic_charge_plan")
        except (ServerFailureException):
            return None

    async def delete_weekly_charge_plan(self):
        """Delete charger basic charge plan setting from cloud"""
        try:
            return await self.easee.delete(f"/api/chargers/{self.id}/weekly_charge_plan")
        except (ServerFailureException):
            return None

    async def override_schedule(self):
        """Override scheduled charging and start charging"""
        try:
            return await self.easee.post(f"/api/chargers/{self.id}/commands/override_schedule")
        except (ServerFailureException):
            return None

    async def smart_charging(self, enable: bool):
        """Set charger smart charging setting"""
        json = {"smartCharging": enable}
        try:
            return await self.easee.post(f"/api/chargers/{self.id}/settings", json=json)
        except (ServerFailureException):
            return None

    async def reboot(self):
        """Reboot charger"""
        try:
            return await self.easee.post(f"/api/chargers/{self.id}/commands/reboot")
        except (ServerFailureException):
            return None

    async def update_firmware(self):
        """Update charger firmware"""
        try:
            return await self.easee.post(f"/api/chargers/{self.id}/commands/update_firmware")
        except (ServerFailureException):
            return None

    async def get_latest_firmware(self):
        """Get the latest released firmeware version"""
        try:
            return await (await self.easee.get(f"/firmware/{self.id}/latest")).json()
        except (ServerFailureException):
            return None

    async def set_dynamic_charger_circuit_current(
        self, currentP1: int, currentP2: int = None, currentP3: int = None, timeToLive: int = 0
    ):
        """Set dynamic current on circuit level. timeToLive specifies, in minutes, for how long the new dynamic current is valid. timeToLive = 0 means that the new dynamic current is valid until changed the next time. The dynamic current is always reset to default when the charger is restarted."""
        if self.circuit is not None:
            return await self.circuit.set_dynamic_current(currentP1, currentP2, currentP3, timeToLive)
        else:
            _LOGGER.info("Circuit info must be initialized for dynamic current to be set")

    async def set_max_charger_circuit_current(self, currentP1: int, currentP2: int = None, currentP3: int = None):
        """Set circuit max current for charger"""
        if self.circuit is not None:
            return await self.circuit.set_max_current(currentP1, currentP2, currentP3)
        else:
            _LOGGER.info("Circuit info must be initialized for max current to be set")

    async def set_max_offline_charger_circuit_current(
        self, currentP1: int, currentP2: int = None, currentP3: int = None
    ):
        """Set circuit max offline current for charger, fallback value for limit if charger is offline"""
        if self.circuit is not None:
            return await self.circuit.set_max_offline_current(currentP1, currentP2, currentP3)
        else:
            _LOGGER.info("Circuit info must be initialized for offline current to be set")

    async def set_dynamic_charger_current(self, current: int, timeToLive: int = 0):
        """Set charger dynamic current"""
        json = {"amps": current, "minutes": timeToLive}
        try:
            return await self.easee.post(f"/api/chargers/{self.id}/commands/set_dynamic_charger_current", json=json)
        except (ServerFailureException):
            return None

    async def set_max_charger_current(self, current: int):
        """Set charger max current"""
        json = {"maxChargerCurrent": current}
        try:
            return await self.easee.post(f"/api/chargers/{self.id}/settings", json=json)
        except (ServerFailureException):
            return None

    async def set_led_strip_brightness(self, brightness: int):
        """Set LED strip brightness."""
        json = {"ledStripBrightness": brightness}
        try:
            return await self.easee.post(f"/api/chargers/{self.id}/settings", json=json)
        except (ServerFailureException):
            return None

    async def set_access(self, access: Union[int, str]):
        """Set the level of access for a changer"""
        json = {
            1: 1,
            2: 2,
            3: 3,
            "open_for_all": 1,
            "easee_account_required": 2,
            "whitelist": 3,
        }

        try:
            return await self.easee.put(f"/api/chargers/{self.id}/access", json=json[access])
        except (ServerFailureException):
            return None

    async def delete_access(self):
        """Revert permissions overridden on a charger level"""
        try:
            return await self.easee.delete(f"/api/chargers/{self.id}/access")
        except (ServerFailureException):
            return None

    async def force_update_lifetimeenergy(self):
        """Forces charger to update Lifetime Energy reading to the cloud. Warning: Rate limited to once every 3 minutes."""
        try:
            return await self.easee.post(f"/api/chargers/{self.id}/commands/poll_lifetimeenergy")
        except (ServerFailureException):
            return None

    async def force_update_opmode(self):
        """Forces charger to update Op Mode to the cloud. Warning: Rate limited to once every 3 minutes."""
        try:
            return await self.easee.post(f"/api/chargers/{self.id}/commands/poll_chargeropmode")
        except (ServerFailureException):
            return None

    async def get_ocpp_config(self):
        """Reads the OCPP config of the charger"""
        try:
            return await (await self.easee.get(f"/local-ocpp/v1/connection-details/{self.id}")).json()
        except (NotFoundException):
            return None
        except (ServerFailureException):
            return None

    async def set_ocpp_config(self, enable, url):
        """Writes the OCPP config of the charger"""
        if enable:
            enablestr = "DualProtocol"
        else:
            enablestr = "OcppOff"
        json = {"connectivityMode": enablestr, "websocketConnectionArgs": {"url": url}}
        try:
            result = await (await self.easee.post(f"/local-ocpp/v1/connection-details/{self.id}", json=json)).json()
            return result["version"]
        except (ServerFailureException):
            return None

    async def apply_ocpp_config(self, version):
        """Applies a stored OCPP config of the charger"""
        json = {"version": version}
        try:
            return await (await self.easee.post(f"/local-ocpp/v1/connections/chargers/{self.id}", json=json)).json()
        except (ServerFailureException):
            return None
