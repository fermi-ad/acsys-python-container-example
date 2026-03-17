#!/usr/bin/env python3

import argparse
import logging
import queue
import sys
import threading
import time

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

UI_REFRESH_FPS = 30
UI_REFRESH_MS = int(1000 / UI_REFRESH_FPS)


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
        sctime_count = 0
        got_outtmp = None

        async for evt_res in dpm:
            # Print OUTTMP and the first 5 SCTIME readings
            if got_outtmp and sctime_count >= 5:
                return
            if evt_res.is_reading_for(0) and not got_outtmp:
                got_outtmp = True
                print(evt_res)
            elif evt_res.is_reading_for(1):
                sctime_count += 1
                if sctime_count <= 5:
                    print(evt_res)


async def stream_sctime(con, update_queue: queue.Queue, stop_event: threading.Event):
    async with acsys.dpm.DPMContext(con) as dpm:
        await dpm.add_entry(1, "G:SCTIME@P,15H")
        await dpm.start()

        log_every_seconds = 5.0
        next_log_at = time.monotonic() + log_every_seconds
        msg_count = 0

        async for evt_res in dpm:
            if stop_event.is_set():
                break

            if evt_res.is_reading_for(1):
                payload = str(evt_res)
                update_queue.put(payload)
                msg_count += 1

                now = time.monotonic()
                if now >= next_log_at:
                    print(f"SCTIME stream active ({msg_count} updates received)")
                    next_log_at = now + log_every_seconds


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
            acsys.run_client(my_app)
        except KeyboardInterrupt:
            return
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
        timer.start(UI_REFRESH_MS)

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
                window.root.after(UI_REFRESH_MS, pump_updates)

        def on_close() -> None:
            stop_event.set()
            window.root.destroy()

        window.root.protocol("WM_DELETE_WINDOW", on_close)
        window.root.after(UI_REFRESH_MS, pump_updates)
        window.root.mainloop()
        stop_event.set()


if __name__ == "__main__":
    main()
