import html
import sys

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


def show_pyqt_output(data: dict | None):
    if QApplication is None:
        raise RuntimeError("PyQt6 is not installed. Install it with: uv add PyQt6")

    app = QApplication(sys.argv)
    window = OutputWindow(data)
    window.show()
    app.exec()
