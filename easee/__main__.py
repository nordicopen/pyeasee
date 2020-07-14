import sys
import asyncio
import logging
from .easee import Easee
from .charger import Charger
from .site import Site

logging.basicConfig(
    format="%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s", level=logging.INFO
)

_LOGGER = logging.getLogger(__name__)


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


if __name__ == "__main__":
    import time

    s = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")
