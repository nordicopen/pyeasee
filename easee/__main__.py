import sys
import asyncio
import logging
from .easee import Easee, Charger


logging.basicConfig(
    format="%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s", level=logging.INFO
)

_LOGGER = logging.getLogger(__name__)


async def main():
    _LOGGER.info("Logging in using: %s %s", sys.argv[1], sys.argv[2])
    easee = Easee(sys.argv[1], sys.argv[2])
    chargers = await easee.get_chargers()
    tasks = [c.async_update() for c in chargers]
    if tasks:
        await asyncio.wait(tasks)
    _LOGGER.info("Chargers: %s", [str(c) for c in chargers])
    await easee.close()


if __name__ == "__main__":
    import time

    s = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")
