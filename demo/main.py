#!/usr/bin/env python3

import argparse
import logging
import queue
import sys
import threading

import acsys
import acsys.dpm
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from pyqt_ui import OutputWindow as PyQtOutputWindow
from reading_parser import parse_flexible_mapping
from tkinter_ui import OutputWindow as TkOutputWindow

_log = logging.getLogger("acsys")
_log.setLevel("DEBUG")
handler = logging.StreamHandler(sys.stdout)
_log.addHandler(handler)


async def my_app(con):
    # Setup context
    async with acsys.dpm.DPMContext(con) as dpm:
        # Add acquisition requests
        # One-time request
        await dpm.add_entry(0, "M:OUTTMP")
        # Repeated requests at 15Hz
        await dpm.add_entry(1, "G:SCTIME@P,15H")

        # Start acquisition
        await dpm.start()

        # Process incoming data
        got_outtmp = None
        latest_sctime = None
        async for evt_res in dpm:
            if evt_res.is_reading_for(0) and got_outtmp is None:
                got_outtmp = str(evt_res)
                print(evt_res)
            elif evt_res.is_reading_for(1):
                latest_sctime = str(evt_res)
                print(evt_res)

            if got_outtmp is not None and latest_sctime is not None:
                return latest_sctime

        return latest_sctime or got_outtmp or "No reading received."


async def stream_sctime(con, update_queue: queue.Queue, stop_event: threading.Event):
    async with acsys.dpm.DPMContext(con) as dpm:
        await dpm.add_entry(1, "G:SCTIME@P,15H")
        await dpm.start()

        async for evt_res in dpm:
            if stop_event.is_set():
                break

            if evt_res.is_reading_for(1):
                payload = str(evt_res)
                update_queue.put(payload)
                print(evt_res)


def main():
    parser = argparse.ArgumentParser(description="Fetch and display one ACSys reading.")
    parser.add_argument(
        "--ui",
        choices=["pyqt", "tkinter"],
        help="Display output in a desktop UI (pyqt or tkinter).",
    )
    args = parser.parse_args()

    if args.ui is None:
        try:
            output = acsys.run_client(my_app)
        except KeyboardInterrupt:
            return

        parsed = parse_flexible_mapping(output)
        print(parsed if parsed is not None else output)
        return

    updates: queue.Queue[str] = queue.Queue()
    stop_event = threading.Event()

    def run_stream() -> None:
        try:
            acsys.run_client(lambda con: stream_sctime(con, updates, stop_event))
        except Exception:
            _log.exception("SCTIME stream stopped unexpectedly")

    stream_thread = threading.Thread(target=run_stream, daemon=True)
    stream_thread.start()

    if args.ui == "pyqt":
        app = QApplication(sys.argv)
        window = PyQtOutputWindow(None)

        timer = QTimer()

        def pump_updates() -> None:
            latest_payload = None
            while not updates.empty():
                latest_payload = updates.get_nowait()
            if latest_payload is not None:
                window.update_data(parse_flexible_mapping(latest_payload))

        timer.timeout.connect(pump_updates)
        timer.start(66)

        def on_about_to_quit() -> None:
            stop_event.set()

        app.aboutToQuit.connect(on_about_to_quit)
        window.show()
        app.exec()
        stop_event.set()

    elif args.ui == "tkinter":
        window = TkOutputWindow(None)

        def pump_updates() -> None:
            latest_payload = None
            while not updates.empty():
                latest_payload = updates.get_nowait()
            if latest_payload is not None:
                window.update_data(parse_flexible_mapping(latest_payload))
            if not stop_event.is_set():
                window.root.after(66, pump_updates)

        def on_close() -> None:
            stop_event.set()
            window.root.destroy()

        window.root.protocol("WM_DELETE_WINDOW", on_close)
        window.root.after(66, pump_updates)
        window.root.mainloop()
        stop_event.set()


if __name__ == "__main__":
    main()
