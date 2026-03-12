#!/usr/bin/env python3

import argparse
import logging
import sys

import acsys
import acsys.dpm

from reading_parser import parse_flexible_mapping
from pyqt_ui import show_pyqt_output
from tkinter_ui import show_tk_output

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
                print(evt_res)
                return str(evt_res)

    return "No reading received."


def main():
    parser = argparse.ArgumentParser(description="Fetch and display one ACSys reading.")
    parser.add_argument(
        "--ui",
        choices=["pyqt", "tkinter"],
        help="Display output in a desktop UI (pyqt or tkinter).",
    )
    args = parser.parse_args()

    output = acsys.run_client(my_app)
    parsed = parse_flexible_mapping(output)

    if args.ui == "pyqt":
        print("[main] launching PyQt UI")
        show_pyqt_output(parsed)
    elif args.ui == "tkinter":
        show_tk_output(parsed)


if __name__ == "__main__":
    main()
