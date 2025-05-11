![Maintenance](https://img.shields.io/maintenance/yes/2025.svg)

# Easee EV Charger library

This library is an async thin wrapper around [Easee's Rest API](https://developer.easee.com/reference/post_api-accounts-login)

## Installation

You can install the libray from [PyPI](https://pypi.org/project/pyeasee/):

    pip install pyeasee

The library is tested on Python 3.13

## Command line tool

Run `python -m pyeasee -h` for help.

## Usage of the library

### Docs

Read the API documentation [here](https://nordicopen.github.io/pyeasee/pyeasee/)

### Small example

Save the example to a file and run it like this: python3 example.py <username> <password>
Username is the phone number that was used to register the Easee account with country code.
E.g. +46xxxxxxxxx.

```python
import asyncio
import sys
from pyeasee import Easee

async def async_main():

    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <username> <password>")
        return

    print(f"Logging in using: {sys.argv[1]} {sys.argv[2]}")
    easee = Easee(sys.argv[1], sys.argv[2])

    sites = await easee.get_sites()
    for site in sites:
        print(f"Site {site.name} ({site.id})")
        equalizers = site.get_equalizers()
        for equalizer in equalizers:
            print(f"  Equalizer: {equalizer.name} ({equalizer.id})")
        circuits = site.get_circuits()
        for circuit in circuits:
            print(f"  Circuit {circuit.id}")
            chargers = circuit.get_chargers()
            for charger in chargers:
                state = await charger.get_state()
                print(f"    Charger: {charger.name} ({charger.id}) status: {state['chargerOpMode']}")

    await easee.close()

asyncio.run(async_main())
```

See also [\_\_main\_\_.py](https://github.com/nordicopen/pyeasee/blob/master/pyeasee/__main__.py) for a more complete usage example.

## Development

This project uses `black` for code formatting and `flake8` for linting. To autoformat and run lint run

```
make lint
```

## Attribution, support and cooperation

This project was started by the late Niklas Fondberg, @fondberg. The repository has been inherited by his collaborators.
