import asyncio
import json
import logging
import argparse
from typing import List

from . import Easee, Charger, Site, Circuit, Equalizer


CACHED_TOKEN = "easee-token.json"

_LOGGER = logging.getLogger(__file__)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Read data from your Easee EV installation")
    parser.add_argument("-u", "--username", help="Username", required=True)
    parser.add_argument("-p", "--password", help="Password", required=True)
    parser.add_argument("-c", "--chargers", help="Get chargers information", action="store_true")
    parser.add_argument("-s", "--sites", help="Get sites information", action="store_true")
    parser.add_argument("-ci", "--circuits", help="Get circuits information", action="store_true")
    parser.add_argument("-e", "--equalizers", help="Get equalizers information", action="store_true")
    parser.add_argument(
        "-a", "--all", help="Get all sites, circuits, equalizers and chargers information", action="store_true",
    )
    parser.add_argument(
        "-sum",
        "--summary",
        help="Get summary of sites, circuits, equalizers and chargers information",
        action="store_true",
    )
    parser.add_argument("-l", "--loop", help="Loop charger data every 5 seconds", action="store_true")
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
        "-v", "--verbose", help="Be verbose", action="store_const", dest="loglevel", const=logging.INFO,
    )
    args = parser.parse_args()
    logging.basicConfig(
        format="%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s", level=args.loglevel,
    )
    return args


# TODO: Add option to send in a cached token
# def token_read():
#     try:
#         with open(CACHED_TOKEN, "r") as token_file:
#             return json.load(token_file)
#     except FileNotFoundError:
#         return None


# def token_write(token):
#     with open(CACHED_TOKEN, "w") as token_file:
#         json.dump(token, token_file, indent=2)


async def main():
    args = parse_arguments()
    _LOGGER.debug("args: %s", args)
    easee = Easee(args.username, args.password)
    if args.chargers:
        chargers: List[Charger] = await easee.get_chargers()
        await chargers_info(chargers)

    if args.sites:
        sites: List[Site] = await easee.get_sites()
        await sites_info(sites)

    if args.circuits:
        sites: List[Site] = await easee.get_sites()
        for site in sites:
            await circuits_info(circuits=site.get_circuits())

    if args.equalizers:
        sites: List[Site] = await easee.get_sites()
        for site in sites:
            await equalizers_info(equalizers=site.get_equalizers())

    if args.countries:
        countries_active = await easee.get_active_countries()
        print(json.dumps(countries_active, indent=2))

    if args.all:
        sites: List[Site] = await easee.get_sites()
        await sites_info(sites)
        for site in sites:
            equalizers = site.get_equalizers()
            await equalizers_info(equalizers)
            circuits = site.get_circuits()
            await circuits_info(circuits)
            for circuit in circuits:
                chargers = circuit.get_chargers()
                await chargers_info(chargers)

    if args.summary:
        sites: List[Site] = await easee.get_sites()
        circuits = List[Circuit]
        chargers = List[Charger]
        equalizers = List[Equalizer]

        for site in sites:
            print(
                f"  "
                f" Site: {site.__getitem__('name')}"
                f" (ID: {site.id}),"
                f" {site.__getitem__('address')['street']},"
                f" main fuse {site.__getitem__('ratedCurrent')}A"
                f" "
            )
            equalizers = site.get_equalizers()
            for equalizer in equalizers:
                print(
                    f"    "
                    f" Equalizer: #{equalizer.__getitem__('name')}"
                    f" (ID: {equalizer.id})"
                    f" SiteID: #{equalizer.__getitem__('siteId')}"
                    f" CircuitId: #{equalizer.__getitem__('circuitId')}"
                    f" "
                )
            circuits = site.get_circuits()
            for circuit in circuits:
                print(
                    f"    "
                    f" Circuit: #{circuit.__getitem__('circuitPanelId')}"
                    f" {circuit.__getitem__('panelName')}"
                    f" (ID: {circuit.id})"
                    f" {circuit.__getitem__('ratedCurrent')}A"
                    f" "
                )
                chargers = circuit.get_chargers()
                for charger in chargers:
                    state = await charger.get_state()
                    config = await charger.get_config()
                    print(
                        f"      "
                        f" Charger: {charger.__getitem__('name')}"
                        f" (ID: {charger.id}),"
                        f" enabled: {config.__getitem__('isEnabled')}"
                        f" online: {state.__getitem__('isOnline')}"
                        f" version: {state.__getitem__('chargerFirmware')}"
                        f" voltage: {round(state.__getitem__('voltage'),1)}"
                        f" current: {round(state.__getitem__('outputCurrent'),1)}"
                        f" "
                    )

        print(f"\n\nFound {len(sites)} site(s), {len(circuits)} circuit(s) and {len(chargers)} charger(s).")

    if args.loop:
        sites: List[Site] = await easee.get_sites()
        for site in sites:
            circuits = site.get_circuits()
            for circuit in circuits:
                chargers = circuit.get_chargers()
                try:
                    header = True
                    while True:
                        for charger in chargers:
                            await charger_loop(charger, header)
                            header = False
                            await asyncio.sleep(5)
                except KeyboardInterrupt as e:  # noqa
                    # Close connection on user interuption
                    print("Interrupted by user")
                    await easee.close()
                except Exception as e:
                    print(e)
                    await easee.close()

    await easee.close()


async def chargers_info(chargers: List[Charger]):
    print("\n\n****************\nCHARGERS\n****************")
    data = []
    for charger in chargers:
        state = await charger.get_state()
        config = await charger.get_config()
        ch = charger.get_data()
        ch["state"] = state.get_data()
        ch["config"] = config.get_data()
        data.append(ch)

    print(json.dumps(data, indent=2))


async def sites_info(sites: List[Site]):
    print("\n\n****************\nSITES\n****************")
    data = []
    for site in sites:
        data.append(site.get_data())

    print(json.dumps(data, indent=2))


async def circuits_info(circuits: List[Circuit]):
    print("\n\n****************\nCIRCUITS\n****************")
    data = []
    for circuit in circuits:
        data.append(circuit.get_data())

    print(json.dumps(data, indent=2))


async def equalizers_info(equalizers: List[Equalizer]):
    print("\n\n****************\nEQUALIZERS\n****************")
    data = []
    for equalizer in equalizers:
        eq = equalizer.get_data()
        state = await equalizer.get_state()
        eq["state"] = state
        data.append(eq)

    print(json.dumps(data, indent=2,))


async def charger_loop(charger: Charger, header=False):
    """Return the state attributes."""
    # await charger.async_update()
    state = await charger.get_state()
    # config = await charger.get_config() # not used yet

    if header:
        print(str_fixed_length("NAME", 15), end=" ")
        print(str_fixed_length("OPMODE", 20), end=" ")
        print(str_fixed_length("ONLINE", 7), end=" ")
        print(str_fixed_length("POWER", 7), end=" ")
        print(str_fixed_length("OUTCURR", 10), end=" ")
        print(str_fixed_length("IN_T2", 10), end=" ")
        print(str_fixed_length("IN_T3", 10), end=" ")
        print(str_fixed_length("IN_T4", 10), end=" ")
        print(str_fixed_length("IN_T5", 10), end=" ")
        print(str_fixed_length("VOLTAGE", 10), end=" ")
        print(str_fixed_length("kWh", 10), end=" ")
        print(str_fixed_length("RATE", 10), end=" ")
        print(str_fixed_length("REASON", 25), end=" ")
        print(" ")

    print(str_fixed_length(f"{charger.name}", 15), end=" ")
    print(str_fixed_length(f"{state.__getitem__('chargerOpMode')}", 20), end=" ")
    print(str_fixed_length(f"{state.__getitem__('isOnline')}", 7), end=" ")
    print(str_fixed_length(f"{round(state.__getitem__('totalPower'),2)}kW", 7), end=" ")
    print(str_fixed_length(f"{round(state.__getitem__('outputCurrent'),1)}A", 10), end=" ")
    print(str_fixed_length(f"{round(state.__getitem__('inCurrentT2'),1)}A", 10), end=" ")
    print(str_fixed_length(f"{round(state.__getitem__('inCurrentT3'),1)}A", 10), end=" ")
    print(str_fixed_length(f"{round(state.__getitem__('inCurrentT4'),1)}A", 10), end=" ")
    print(str_fixed_length(f"{round(state.__getitem__('inCurrentT5'),1)}A", 10), end=" ")
    print(str_fixed_length(f"{round(state.__getitem__('voltage'),1)}V", 10), end=" ")
    print(
        str_fixed_length(f"{round(state.__getitem__('sessionEnergy'),2)}kWh", 10), end=" ",
    )
    print(
        str_fixed_length(f"{round(state.__getitem__('energyPerHour'),2)}kWh/h", 10), end=" ",
    )
    print(str_fixed_length(f"{str(state.__getitem__('reasonForNoCurrent'))}", 25), end=" ")
    print(" ")


def str_fixed_length(myStr, length: int):
    while len(myStr) < length:
        myStr = myStr + " "
    if len(myStr) > length:
        myStr = myStr[0:length]
    return myStr


if __name__ == "__main__":
    import time

    s = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")
