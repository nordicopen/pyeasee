# Easee EV Charger library

This library is a thin wrapper around [Easee's Rest API](https://api.easee.cloud/index.html)

## Installation

You can install the libray from [PyPI](https://pypi.org/project/easee/):

    pip install easee

The library is tested on Python 3.7 and Python 3.8

## Usage

Easee is the connection class and Charger

```
from easee import Easee, Charger

async def print_chargers():
    easee = Easee("+760111111", "password"])
    chargers = await easee.get_chargers()
    tasks = [c.async_update() for c in chargers]
    await asyncio.wait(tasks)

    _LOGGER.info("Chargers: %s %s", chargers[0].id, chargers[0].state)
    await easee.close()

```
