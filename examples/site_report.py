# Download consumption / session report (PDF) for sites associated with an account
import asyncio
from datetime import datetime, timedelta, timezone
import sys

from pyeasee import Easee, ReportCategory


async def async_main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <username> <password>")
        return

    print(f"Logging in using: {sys.argv[1]} {sys.argv[2]}")
    easee = Easee(sys.argv[1], sys.argv[2])

    now = datetime.now(timezone.utc)
    first_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_prev_month = first_this_month - timedelta(seconds=1)
    first_prev_month = last_prev_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    sites = await easee.get_sites()
    for site in sites:
        print(f"Downloading report for site {site.name} ({site.id})...")
        pdf_bytes = await site.get_report(
            first_prev_month, last_prev_month, category=ReportCategory.CHARGER_DETAILED
        )
        filename = f"report_site_{site.id}_{first_prev_month.strftime('%Y-%m')}.pdf"
        with open(filename, "wb") as f:
            f.write(pdf_bytes)
        print(f"Saved {len(pdf_bytes)} bytes to {filename}")

    await easee.close()


asyncio.run(async_main())
