import html
import os
import platform
import sys

from PyQt6.QtCore import QLibraryInfo
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow

class OutputWindow(QMainWindow):
    def __init__(self, data: dict | None):
        super().__init__()
        self.setWindowTitle("ACSys Output")
        self.resize(480, 160)
        if QLabel is None:
            raise RuntimeError("PyQt6 is not installed. Install it with: uv add PyQt6")

        label = QLabel(self._dict_to_html_list(data) if data is not None else "No reading received.")
        label.setWordWrap(True)
        label.setMargin(16)
        self.setCentralWidget(label)

    def _dict_to_html_list(self, data: dict) -> str:
        def render(value) -> str:
            if isinstance(value, dict):
                items = "".join(
                    f"<li><b>{html.escape(str(k))}</b>: {render(v)}</li>"
                    for k, v in value.items()
                )
                return f"<ul>{items}</ul>"

            if isinstance(value, list):
                items = "".join(f"<li>{render(item)}</li>" for item in value)
                return f"<ul>{items}</ul>"

            return html.escape(str(value))

        return render(data)


def _log_qt_environment() -> None:
    print("[pyqt-ui] starting Qt diagnostics")
    print(f"[pyqt-ui] python={sys.version.split()[0]} platform={platform.platform()}")
    print(f"[pyqt-ui] DISPLAY={os.environ.get('DISPLAY')}")
    print(f"[pyqt-ui] XDG_RUNTIME_DIR={os.environ.get('XDG_RUNTIME_DIR')}")
    print(f"[pyqt-ui] QT_QPA_PLATFORM={os.environ.get('QT_QPA_PLATFORM')}")
    print(f"[pyqt-ui] QT_PLUGIN_PATH={os.environ.get('QT_PLUGIN_PATH')}")
    print(f"[pyqt-ui] Qt plugins path={QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)}")


def show_pyqt_output(data: dict | None):
    if QApplication is None:
        raise RuntimeError("PyQt6 is not installed. Install it with: uv add PyQt6")

    _log_qt_environment()
    app = QApplication(sys.argv)
    window = OutputWindow(data)
    window.show()
    app.exec()
