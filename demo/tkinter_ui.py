import html
import tkinter as tk

class OutputWindow:
    def __init__(self, data: dict | None):
        self.root = tk.Tk()
        self.root.title("ACSys Output")
        self.root.geometry("560x240")

        text_widget = tk.Text(self.root, wrap="word", padx=16, pady=16)
        text_widget.insert(
            "1.0",
            self._dict_to_indented_text(data) if data is not None else "No reading received.",
        )
        text_widget.configure(state="disabled")
        text_widget.pack(fill="both", expand=True)

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
