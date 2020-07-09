# Easee EV Charger library

This library is a thin wrapper around [Easee's Rest API](https://api.easee.cloud/index.html)

## Installation

You can install the libray from [PyPI](https://pypi.org/project/easee/):

    pip install easee

The library is tested on Python 3.7 and Python 3.8

## Usage

Easee is the connection class and Charger

```python
from easee import Easee, Charger

async def get_chargers_info():
    _LOGGER.info("Logging in using: %s %s", sys.argv[1], sys.argv[2])
    easee = Easee(sys.argv[1], sys.argv[2])
    chargers = await easee.get_chargers()
    for charger in chargers:
        state = await charger.get_state()
        _LOGGER.info("Charger: %s status: %s", charger.name, state["chargerOpMode"])
    await easee.close()
```
