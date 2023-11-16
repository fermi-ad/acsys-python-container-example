#!/usr/bin/env python3

import logging
import sys
import acsys.dpm

_log = logging.getLogger('acsys')
_log.setLevel('DEBUG')
handler = logging.StreamHandler(sys.stdout)
_log.addHandler(handler)

async def my_app(con):
    # Setup context
    async with acsys.dpm.DPMContext(con) as dpm:
        # Add acquisition requests
        await dpm.add_entry(0, 'M:OUTTMP')

        # Start acquisition
        await dpm.start()

        # Process incoming data
        async for evt_res in dpm:
            if evt_res.isReading:
                print(evt_res)

            break

def main():
    acsys.run_client(my_app)

if __name__ == '__main__':
    main()
