import sys
import asyncio
import json
import logging
import argparse
from typing import List

from . import Easee, Charger, Site


CACHED_TOKEN = "easee-token.json"

_LOGGER = logging.getLogger(__file__)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Read data from your Easee EV installation")
    parser.add_argument("-u", "--username", help="Username", required=True)
    parser.add_argument("-p", "--password", help="Password", required=True)
    parser.add_argument(
        "-c", "--chargers", help="Get chargers information", action="store_true",
    )
    parser.add_argument("-s", "--sites", help="Get sites information", action="store_true")
    parser.add_argument("--countries", help="Get active countries information", action="store_true")
    parser.add_argument(
        "-d",
        "--debug",
        help="Print debugging statements",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Be verbose",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
    )
    args = parser.parse_args()
    logging.basicConfig(
        format="%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s", level=args.loglevel
    )
    return args


def token_read():
    try:
        with open(CACHED_TOKEN, "r") as token_file:
            return json.load(token_file)
    except FileNotFoundError:
        return None


def token_write(token):
    with open(CACHED_TOKEN, "w") as token_file:
        json.dump(token, token_file, indent=2)


async def main():
    args = parse_arguments()
    _LOGGER.debug("args: %s", args)
    easee = Easee(args.username, args.password)
    if args.chargers:
        chargers: List[Charger] = await easee.get_chargers()
        data = []
        for charger in chargers:
            await charger.async_update()
            data.append(charger.get_data())

        print(json.dumps(data, indent=2,))

    if args.sites:
        sites: List[Site] = await easee.get_sites()
        data = []
        for site in sites:
            data.append(site.get_data())

        await sites[0].set_name("Månvägen Ny")
        print(json.dumps(data, indent=2,))

    if args.countries:
        countries_active = await easee.get_active_countries()
        print(json.dumps(countries_active, indent=2,))

    await easee.close()


if __name__ == "__main__":
    import time

    s = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")
