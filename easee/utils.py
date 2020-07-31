import re
from datetime import datetime, timezone
from collections.abc import Mapping

regex = r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
match_iso8601 = re.compile(regex).match


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
                return datetime.strptime(self._storage[key], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return self._storage[key]

    def __iter__(self):
        return iter(self._storage)  # ``ghost`` is invisible

    def __len__(self):
        return len(self._storage)

    def get_data(self):
        return self._storage
