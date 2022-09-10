![Maintenance](https://img.shields.io/maintenance/yes/2022.svg) ![Easee library](https://github.com/fondberg/easee/workflows/Easee%20library/badge.svg)

[![Buy me a coffee](https://img.shields.io/static/v1.svg?label=Buy%20me%20a%20coffee&message=🥨&color=black&logo=buy%20me%20a%20coffee&logoColor=white&labelColor=6f4e37)](https://www.buymeacoffee.com/fondberg)

# Easee EV Charger library

This library is an async thin wrapper around [Easee's Rest API](https://api.easee.cloud/index.html)

## Installation

You can install the libray from [PyPI](https://pypi.org/project/pyeasee/):

    pip install pyeasee

The library is tested on Python 3.7 and Python 3.8

## Command line tool

Run `python -m pyeasee -h` for help.

## Usage of the library

### Docs

Read the API documentation [here](https://fondberg.github.io/pyeasee/pyeasee/)

### Small example

Copy below script to the `test_pyeasee.py` :

```python
from pyeasee import Easee, Charger, Site
import asyncio
from aiologger import Logger
import os


_LOGGER = Logger.with_default_handlers(name=__name__)


async def list_chargers(chargers):
    """Print out charger state by iterating over charger list"""
    for charger in chargers:
        state = await charger.get_state()
        _LOGGER.info(f"Charger: {charger.name} status: {state['chargerOpMode']}")


async def main():
    user = os.getenv("EASEE_USER", "johndoe")
    passwd = os.getenv("EASEE_PASS", "dummy123")
    # Uncomment below if you want interactive login
    # user = input("Username: ")
    # passwd = input("PAssword: ")

    _LOGGER.info(f"Logging in using: user: {user} pass: {passwd}")
    easee = Easee(user, passwd)
    chargers = await easee.get_chargers()
    await list_chargers(chargers)
    sites = await easee.get_sites()
    for site in sites:
        _LOGGER.info(f"Get sites circuits chargers: {site['createdOn']}")
        chargers_for_site = site.get_circuits()[0].get_chargers()
        await list_chargers(chargers_for_site)

    await easee.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
```

Define the relevant environment variables and then run the script above:
```
export EASEE_USER=<YOUR USER>
export EASE_PASS=<YOUR PASSWORD>
python3 test_pyeasee.py
```

See also [\_\_main\_\_.py](https://github.com/fondberg/pyeasee/blob/master/pyeasee/__main__.py) for a more complete usage example.

## Development

This project uses `black` for code formatting and `flake8` for linting. To autoformat and run lint run

```
make lint
```
