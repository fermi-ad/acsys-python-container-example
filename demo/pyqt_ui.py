import html
import json
import re
import sys

from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow


class OutputWindow(QMainWindow):
    def __init__(self, text: str):
        super().__init__()
        print(text)
        self.setWindowTitle("ACSys Output")
        self.resize(480, 160)
        if QLabel is None:
            raise RuntimeError("PyQt6 is not installed. Install it with: uv add PyQt6")

        rendered_html = self._render_hierarchical_html(text)
        label = QLabel(rendered_html)
        label.setWordWrap(True)
        label.setMargin(16)
        self.setCentralWidget(label)

    def _render_hierarchical_html(self, text: str) -> str:
        parsed = self._parse_flexible_mapping(text)
        if parsed is None:
            return f"<pre>{html.escape(text)}</pre>"

        return self._dict_to_html_list(parsed)

    def _parse_flexible_mapping(self, text: str) -> dict | None:
        try:
            normalized = self._to_valid_json(text)
            parsed = json.loads(normalized)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

        return None

    def _quote_unquoted_top_level_keys(self, text: str) -> str:
        pattern = re.compile(r'([,{]\s*)([A-Za-z_][A-Za-z0-9_\-]*)(\s*:)')

        def replacer(match: re.Match) -> str:
            prefix, key, suffix = match.groups()
            return f'{prefix}"{key}"{suffix}'

        return pattern.sub(replacer, text)

    def _to_valid_json(self, text: str) -> str:
        text = self._quote_unquoted_top_level_keys(text)

        text = re.sub(r'\bNone\b', 'null', text)
        text = re.sub(r'\bTrue\b', 'true', text)
        text = re.sub(r'\bFalse\b', 'false', text)

        text = re.sub(r'"stamp"\s*:\s*([^",}\]][^,}\]]*)', r'"stamp": "\1"', text)

        text = text.replace("'", '"')
        return text

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


def show_pyqt_output(text: str):
    if QApplication is None:
        raise RuntimeError("PyQt6 is not installed. Install it with: uv add PyQt6")

    app = QApplication(sys.argv)
    window = OutputWindow(text)
    window.show()
    app.exec()
