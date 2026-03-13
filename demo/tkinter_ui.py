import html
import tkinter as tk


class OutputWindow:
    def __init__(self, data: dict | None):
        self.root = tk.Tk()
        self.root.title("ACSys Output")
        self.root.geometry("560x320")

        container = tk.Frame(self.root, padx=16, pady=16)
        container.pack(fill="both", expand=True)

        pie_row = tk.Frame(container)
        pie_row.pack(anchor="w")

        self.seconds_canvas = tk.Canvas(
            pie_row, width=110, height=110, highlightthickness=0
        )
        self.seconds_canvas.pack(side="left")

        self.ms_canvas = tk.Canvas(pie_row, width=110, height=110, highlightthickness=0)
        self.ms_canvas.pack(side="left", padx=(12, 0))

        sctime_seconds = self._extract_sctime_seconds(data)
        sctime_ms = (
            (sctime_seconds % 1.0) * 1000 if sctime_seconds is not None else None
        )
        self._draw_pie(self.seconds_canvas, sctime_seconds, 60.0, "#4a90e2")
        self._draw_pie(self.ms_canvas, sctime_ms, 1000.0, "#50c878")

        sctime_ms_text = (
            f"SCTIME: {round(sctime_seconds, 1)} s"
            if sctime_seconds is not None
            else "SCTIME: unavailable"
        )
        self.ms_label = tk.Label(container, text=sctime_ms_text)
        self.ms_label.pack(anchor="w", pady=(6, 12))

        self.text_widget = tk.Text(container, wrap="word", padx=8, pady=8, height=8)
        self.text_widget.insert(
            "1.0",
            self._dict_to_indented_text(data)
            if data is not None
            else "No reading received.",
        )
        self.text_widget.configure(state="disabled")
        self.text_widget.pack(fill="both", expand=True)

    def update_data(self, data: dict | None) -> None:
        sctime_seconds = self._extract_sctime_seconds(data)

        sctime_ms = (
            (sctime_seconds % 1.0) * 1000 if sctime_seconds is not None else None
        )

        self.seconds_canvas.delete("all")
        self.ms_canvas.delete("all")
        self._draw_pie(self.seconds_canvas, sctime_seconds, 60.0, "#4a90e2")
        self._draw_pie(self.ms_canvas, sctime_ms, 1000.0, "#50c878")

        sctime_ms_text = (
            f"SCTIME: {round(sctime_seconds, 1)} s"
            if sctime_seconds is not None
            else "SCTIME: unavailable"
        )
        self.ms_label.configure(text=sctime_ms_text)

        self.text_widget.configure(state="normal")
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(
            "1.0",
            self._dict_to_indented_text(data)
            if data is not None
            else "No reading received.",
        )
        self.text_widget.configure(state="disabled")

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

    def _draw_pie(
        self, canvas: tk.Canvas, value: float | None, max_value: float, color: str
    ) -> None:
        x0, y0, x1, y1 = 5, 5, 105, 105
        canvas.create_oval(x0, y0, x1, y1, outline="#444", width=2, fill="#f0f0f0")

        if value is None or max_value <= 0:
            return

        clamped = max(0.0, min(max_value, value))
        extent = 360.0 * (clamped / max_value)
        if extent <= 0:
            return

        canvas.create_arc(
            x0,
            y0,
            x1,
            y1,
            start=90,
            extent=-extent,
            fill=color,
            outline=color,
            style=tk.PIESLICE,
        )

    def _dict_to_indented_text(self, data: dict) -> str:
        def render(value, indent: int = 0) -> str:
            prefix = "  " * indent

            if isinstance(value, dict):
                lines = []
                for k, v in value.items():
                    if isinstance(v, (dict, list)):
                        lines.append(f"{prefix}{k}:")
                        lines.append(render(v, indent + 1))
                    else:
                        lines.append(f"{prefix}{k}: {html.unescape(str(v))}")
                return "\n".join(lines)

            if isinstance(value, list):
                lines = []
                for item in value:
                    if isinstance(item, (dict, list)):
                        lines.append(f"{prefix}-")
                        lines.append(render(item, indent + 1))
                    else:
                        lines.append(f"{prefix}- {html.unescape(str(item))}")
                return "\n".join(lines)

            return f"{prefix}{html.unescape(str(value))}"

        return render(data)


def show_tk_output(data: dict | None):
    window = OutputWindow(data)
    window.root.mainloop()
