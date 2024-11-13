# List consumption per user for all sites assosiated with an account
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
        users = await site.get_users()
        for user in users["siteUsers"]:
            print(f"  User {user['userId']}: {user['name']}, {user['email']}")
            consumptions = await site.get_user_monthly_consumption(user["userId"])
            for consumption in consumptions:
                print(f"    {consumption['year']}-{consumption['month']}: {consumption['totalEnergyUsage']} kWh")

    await easee.close()


asyncio.run(async_main())
