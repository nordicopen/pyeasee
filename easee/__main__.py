from easee.site import Circuit
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
    parser.add_argument("-s", "--site", help="Get site information", action="store_true")
    parser.add_argument("-a", "--all", help="Populate all: site, circuits and chargers from logged in account", action="store_true")    
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
    await easee.populate()    
    chargers: List[Charger] = easee.get_chargers()
    sites: List[Site] = easee.get_sites()
    circuits: List[Circuit] = easee.get_circuits()

    if args.chargers:
        data = []
        for charger in chargers:
            await charger.async_update()
            data.append(charger.get_data())
        print(json.dumps(data, indent=2,))

    if args.site:
        data = []
        for site in sites:
            data.append(site.get_data())

        print(json.dumps(data, indent=2,))

    if args.all:
        for site in sites:
            print(f"Site - ID: {site['id']} Name: {site['name']} with {site.get_number_of_chargers()} chargers")
            for circuit in circuits:
                print(f"   Circuit - ID: {circuit['id']} Name: {circuit.get_name()}")
                for charger in chargers:
                    print(f"      Charger - ID: {charger['id']} Name: {charger['name']}")

                    # await charger.set_circuit_dynamicCurrent(7)
                    # await charger.set_circuit_maxcurrent(12)
    if args.countries:
        countries_active = await easee.get_active_countries()
        print(json.dumps(countries_active, indent=2,))

    if args.loop:
        if easee.get_sites() is None:
            await easee.populate()
        try:
            header = True
            while True:
                chargers = easee.get_chargers()            
                for c in chargers:
                    await running_in_loop(c, header)
                    header = False
                    time.sleep(5)    
        except KeyboardInterrupt as ki:
            # Close connection on user interuption
            print("Interrupted")
            await easee.close()
        except Exception as e:
            print(e)
            await easee.close()
    await easee.close()


async def running_in_loop(charger :Charger, header=False):
    """Return the state attributes."""
    await charger.async_update()

    if header:
    if header:
        print(f"{'NAME':<15}", end=" ")
        print(f"{'OPMODE':<20}", end=" ")    
        print(f"{'ONLINE':<7}", end=" ")        
        print(f"{'POWER':<7}", end=" ")        
        print(f"{'OUTCURR':<10}", end=" ")        
        print(f"{'IN_T2':<10}", end=" ")        
        print(f"{'IN_T3':<10}", end=" ")        
        print(f"{'IN_T4':<10}", end=" ")        
        print(f"{'VOLTAGE':<10}", end=" ")        
        print(f"{'kWh':<10}", end=" ")        
        print(f"{'RATE':<10}", end=" ")                
        print(f"{'REASON':<25}", end=" ")        
        print(" ")

    print(printme(f"{charger.get_name()}",15), end=" ")
    print(printme(f"{charger.get_cached_state_entry('chargerOpMode')}",20), end=" ")
    print(printme(f"{charger.get_cached_state_entry('isOnline')}",7), end=" ")
    print(printme(f"{round(charger.get_cached_state_entry('totalPower'),2)}kW",7), end=" ")
    print(printme(f"{round(charger.get_cached_state_entry('outputCurrent'),1)}A",10), end=" ")
    print(printme(f"{round(charger.get_cached_state_entry('inCurrentT2'),1)}A",10), end=" ")
    print(printme(f"{round(charger.get_cached_state_entry('inCurrentT3'),1)}A",10), end=" ")
    print(printme(f"{round(charger.get_cached_state_entry('inCurrentT4'),1)}A",10), end=" ")
    print(printme(f"{round(charger.get_cached_state_entry('inCurrentT5'),1)}A",10), end=" ")
    print(printme(f"{round(charger.get_cached_state_entry('voltage'),2)}V",10), end=" ")
    print(printme(f"{round(charger.get_cached_state_entry('sessionEnergy'),2)}kWh",10), end=" ")
    print(printme(f"{round(charger.get_cached_state_entry('energyPerHour'),2)}kWh/h",10), end=" ")
    print(printme(f"{str(charger.get_cached_state_entry('reasonForNoCurrent'))}",25), end=" ")
    print(" ")

def printme(myStr, length:int):
    while len(myStr)<length:
        myStr = myStr +" "
    if len(myStr)>length:
        myStr = myStr[0:length]
    return myStr

if __name__ == "__main__":
    import time

    s = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")
