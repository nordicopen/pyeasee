from collections.abc import Mapping
from datetime import datetime, timezone
import re

from .const import ChargerStreamData, EqualizerStreamData

regex = r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
match_iso8601 = re.compile(regex).match


def lookup_charger_stream_id(id):
    try:
        name = ChargerStreamData(id).name
    except ValueError:
        return None
    return name


def lookup_equalizer_stream_id(id):
    try:
        name = EqualizerStreamData(id).name
    except ValueError:
        return None
    return name


def convert_stream_data(data_type, value):
    if data_type == 2:
        if value.lower() in ["1", "true", "on", "yes"]:
            return True
        else:
            return False
    elif data_type == 3:
        return float(value)
    elif data_type == 4:
        return int(value)

    return value


def validate_iso8601(str_val):
    try:
        if match_iso8601(str_val) is not None:
            return True
    except Exception:
        pass
    return False


class BaseDict(Mapping):
    def __init__(self, entries):
        self._storage = entries

    def __getitem__(self, key):
        if type(self._storage[key]) == str and validate_iso8601(self._storage[key]):
            try:
                return datetime.fromisoformat(self._storage[key]).replace(tzinfo=timezone.utc)
            except ValueError:
                try:
                    return datetime.strptime(self._storage[key], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                except ValueError:
                    (dt, msecs) = self._storage[key].split(".")
                    return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        return self._storage[key]

    def __setitem__(self, key, value):
        self._storage[key] = value

    def __iter__(self):
        return iter(self._storage)  # ``ghost`` is invisible

    def __len__(self):
        return len(self._storage)

    def get_data(self):
        return self._storage
