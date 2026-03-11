#!/usr/bin/env python3

import argparse
import logging
import sys

import acsys
import acsys.dpm

from pyqt_ui import show_pyqt_output

_log = logging.getLogger("acsys")
_log.setLevel("DEBUG")
handler = logging.StreamHandler(sys.stdout)
_log.addHandler(handler)


async def my_app(con):
    # Setup context
    async with acsys.dpm.DPMContext(con) as dpm:
        # Add acquisition requests
        await dpm.add_entry(0, "M:OUTTMP")

        # Start acquisition
        await dpm.start()

        # Process incoming data
        async for evt_res in dpm:
            if evt_res.isReading:
                return str(evt_res)

    return "No reading received."


def main():
    parser = argparse.ArgumentParser(description="Fetch and display one ACSys reading.")
    parser.add_argument(
        "--ui",
        action="store_true",
        help="Display output in a simple PyQt window.",
    )
    args = parser.parse_args()

    output = acsys.run_client(my_app)

    if args.ui:
        show_pyqt_output(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
