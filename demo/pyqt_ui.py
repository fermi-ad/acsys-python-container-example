import html
import sys

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)


class PieWidget(QWidget):
    def __init__(self, value: float | None, max_value: float, color: str = "#4a90e2"):
        super().__init__()
        self.value = value
        self.max_value = max_value
        self.color = color
        self.setMinimumSize(120, 120)

    def set_value(self, value: float | None) -> None:
        self.value = value
        self.update()

    def paintEvent(self, a0):
        _ = a0
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(
            10,
            10,
            min(self.width(), self.height()) - 20,
            min(self.width(), self.height()) - 20,
        )
        painter.setPen(QPen(QColor("#444"), 2))
        painter.setBrush(QColor("#f0f0f0"))
        painter.drawEllipse(rect)

        if self.value is None or self.max_value <= 0:
            return

        clamped = max(0.0, min(self.max_value, self.value))
        span_degrees = 360.0 * (clamped / self.max_value)
        if span_degrees <= 0:
            return

        painter.setPen(QPen(QColor(self.color), 1))
        painter.setBrush(QColor(self.color))
        painter.drawPie(rect, 90 * 16, int(-span_degrees * 16))


class OutputWindow(QMainWindow):
    def __init__(self, data: dict | None):
        super().__init__()
        self.setWindowTitle("ACSys Output")
        self.resize(560, 320)
        if QLabel is None:
            raise RuntimeError("PyQt6 is not installed. Install it with: uv add PyQt6")

        sctime_seconds = self._extract_sctime_seconds(data)
        sctime_ms = (
            (sctime_seconds % 1.0) * 1000 if sctime_seconds is not None else None
        )

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        pie_row = QHBoxLayout()
        pie_row.setSpacing(12)

        self.pie_seconds = PieWidget(sctime_seconds, 60.0, "#4a90e2")
        self.pie_seconds.setMaximumSize(120, 120)
        pie_row.addWidget(self.pie_seconds)

        self.pie_milliseconds = PieWidget(sctime_ms, 1000.0, "#50c878")
        self.pie_milliseconds.setMaximumSize(120, 120)
        pie_row.addWidget(self.pie_milliseconds)

        pie_row_container = QWidget()
        pie_row_container.setLayout(pie_row)
        layout.addWidget(pie_row_container, alignment=Qt.AlignmentFlag.AlignLeft)

        ms_label_text = (
            f"SCTIME: {round(sctime_seconds * 1000)} ms"
            if sctime_seconds is not None
            else "SCTIME: unavailable"
        )
        self.ms_label = QLabel(ms_label_text)
        layout.addWidget(self.ms_label)

        self.detail_label = QLabel(
            self._dict_to_html_list(data)
            if data is not None
            else "No reading received."
        )
        self.detail_label.setWordWrap(True)
        layout.addWidget(self.detail_label)

        self.setCentralWidget(root)

    def update_data(self, data: dict | None) -> None:
        sctime_seconds = self._extract_sctime_seconds(data)
        sctime_ms = (
            (sctime_seconds % 1.0) * 1000 if sctime_seconds is not None else None
        )
        self.pie_seconds.set_value(sctime_seconds)
        self.pie_milliseconds.set_value(sctime_ms)

        ms_label_text = (
            f"SCTIME: {round(sctime_seconds, 1)} s"
            if sctime_seconds is not None
            else "SCTIME: unavailable"
        )
        self.ms_label.setText(ms_label_text)
        self.detail_label.setText(
            self._dict_to_html_list(data)
            if data is not None
            else "No reading received."
        )

    def _extract_sctime_seconds(self, data: dict | None) -> float | None:
        if not isinstance(data, dict):
            return None

        raw = data.get("data")
        if isinstance(raw, (int, float)):
            return float(raw)

        if isinstance(raw, str):
            try:
                return float(raw)
            except ValueError:
                return None

        return None

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
