import asyncio
import sys
from pyeasee import Easee
from datetime import datetime, timezone, timedelta
import polars as pl

async def async_main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <username> <password>")
        return

    print(f"Logging in using: {sys.argv[1]} {sys.argv[2]}")
    easee = Easee(sys.argv[1], sys.argv[2])

    sites = await easee.get_sites()
    for site in sites:
        print(f"Site {site.name} ({site.id})")
        circuits = site.get_circuits()
        all_dfs = []
        for circuit in circuits:
            chargers = circuit.get_chargers()
            for charger in chargers:
                # Some chargers return an error
                try:
                    state = await charger.get_state()
                except Exception as e:
                    print(f"    Error getting state for charger {charger.name} ({charger.id}): {e}")
                    continue
                # Fetch one month at a time, as the API limits the requested time period
                charger_consumption = []
                year = 2025
                for month in range(1 , 13):
                    from_date = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
                    if month == 12:
                        to_date = datetime(year + 1 , 1, 1, 0, 0, 0, tzinfo=timezone.utc)
                    else:
                        to_date = datetime(year, month + 1, 1, 0, 0, 0, tzinfo=timezone.utc)
                    if to_date > datetime.now(timezone.utc):
                        to_date = datetime.now(timezone.utc)
                    if from_date >= to_date:
                        continue
                    print(f"    Getting Charger: {charger.name} ({charger.id}) between {from_date} and {to_date}")
                    consumption = await charger.get_hourly_consumption_between_dates(from_date, to_date)
                    charger_consumption.extend(consumption)
                print(f"    Total hours collected: {len(charger_consumption)}")
                if charger_consumption:
                    df = pl.DataFrame(charger_consumption)
                    df = df.with_columns([
                        pl.col("from").str.to_datetime().dt.replace_time_zone(None).alias("datetime"),
                        pl.lit(charger.id).alias("chargerId")
                    ])
                    df = df.drop(["from", "to"])
                    all_dfs.append(df)
                    
        if all_dfs:
            site_consumption = pl.concat(all_dfs)
            site_consumption.write_csv(f"hourly_consumption_{site.id}.csv")
            sum_df = site_consumption.group_by("datetime").agg(
                pl.col("totalEnergy").sum(),
            )
            sum_df.write_excel(f"hourly_consumption_aggregate_{site.id}.xlsx")
            print("Data written to hourly_consumption_{site.id}.csv and hourly_consumption_aggregate_{site.id}.xlsx")                
    await easee.close()

asyncio.run(async_main())