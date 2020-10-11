![Maintenance](https://img.shields.io/maintenance/yes/2020.svg) ![Easee library](https://github.com/fondberg/easee/workflows/Easee%20library/badge.svg)

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

Easee is the connection class and Charger

```python
from pyeasee import Easee, Charger, Site

async def main():
    _LOGGER.info("Logging in using: %s %s", sys.argv[1], sys.argv[2])
    easee = Easee(sys.argv[1], sys.argv[2])
    chargers = await easee.get_chargers()
    for charger in chargers:
        state = await charger.get_state()
        _LOGGER.info("Charger: %s status: %s", charger.name, state["chargerOpMode"])

    sites = await easee.get_sites()
    for site in sites:
        _LOGGER.info("Get sites circuits chargers: %s", site["createdOn"])
        charger = site.get_circuits()[0].get_chargers()[0]
        state = await charger.get_state()
        _LOGGER.info("Charger: %s status: %s", charger.name, state["chargerOpMode"])

    await easee.close()
```

## Development

This project uses `black` for code formatting and `flake8` for linting. To autoformat and run lint run

```
make lint
```
