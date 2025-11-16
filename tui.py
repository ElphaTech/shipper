from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Button, ContentSwitcher, Markdown, Label

from functions.t_status import StatusTable, OverviewTable
from functions.t_info import DiskSpaceBar

MARKDOWN_EXAMPLE = """# Potential docs?"""


class ContentSwitcherApp(App[None]):
    CSS_PATH = "css/textual.tcss"
    BINDINGS = []

    def compose(self) -> ComposeResult:
        with Horizontal(id="buttons"):
            yield Button("Jobs", id="status-table")
            yield Button("Overview", id="overview-table")
            yield Button("Docs", id="markdown")

        with ContentSwitcher(initial="status-table"):
            yield StatusTable(id="status-table")
            yield OverviewTable(id="overview-table")
            with VerticalScroll(id="markdown"):
                yield Markdown(MARKDOWN_EXAMPLE)

        yield Label("Disk Space")
        yield DiskSpaceBar(id="disk-space-bar", show_eta=False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.query_one(ContentSwitcher).current = event.button.id


if __name__ == "__main__":
    ContentSwitcherApp().run()
